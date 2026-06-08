"""
State Extractor
---------------
Extracts a clean, LLM-friendly snapshot of the current page state.
Focuses on what is ACTUALLY VISIBLE in the current viewport.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PageState:
    url:               str
    title:             str
    viewport_elements: list[str] = field(default_factory=list)
    has_overlay:       bool      = False
    overlay_text:      str       = ""
    scroll_position:   int       = 0
    page_height:       int       = 0
    at_bottom:         bool      = False
    visible_text:      str       = ""   # raw text visible in the current viewport
    # True when a search input is focused AND already has typed text — means the
    # search suggestion drawer is likely open.  NOT an overlay; handled separately.
    search_suggestions_active: bool = False

    def elements_block(self) -> str:
        if not self.viewport_elements:
            return "  (no interactive elements detected in viewport)"
        lines = []
        for i, el in enumerate(self.viewport_elements, 1):
            lines.append(f"  [{i}] {el}")
        return "\n".join(lines)

    def scroll_context(self) -> str:
        if self.page_height <= 0:
            return ""
        pct = min(100, int((self.scroll_position / max(1, self.page_height - 800)) * 100))
        if self.at_bottom:
            return "  (you are at the BOTTOM of the page — no more content below)"
        if self.scroll_position < 50:
            return "  (you are at the TOP of the page)"
        return f"  (you have scrolled ~{pct}% down the page)"


# ── JS that extracts visible interactive elements from the current viewport ────
# Returns up to 50 elements as strings like "[LINK] Personal Loan"

_VIEWPORT_ELEMENTS_JS = """
() => {
    const vpH = window.innerHeight;
    const vpW = window.innerWidth;
    const results = [];
    const seen = new Set();   // keyed by normalised text to avoid duplicates

    function inViewport(rect) {
        return rect.bottom > 4 && rect.top < vpH - 4 &&
               rect.right  > 4 && rect.left < vpW - 4 &&
               rect.width >= 4 && rect.height >= 4;
    }

    function isVisible(style) {
        return style.display !== 'none' &&
               style.visibility !== 'hidden' &&
               parseFloat(style.opacity) >= 0.1;
    }

    function getText(el) {
        // Cascade: aria-label → title → innerText → child-img alt → placeholder/value/alt
        const candidates = [
            el.getAttribute('aria-label'),
            el.getAttribute('title'),
            (el.innerText || '').trim(),
        ];
        // Image-only links/buttons: read the child <img alt>
        const img = el.querySelector('img');
        if (img) candidates.push(img.getAttribute('alt'));
        candidates.push(
            el.getAttribute('placeholder'),
            el.getAttribute('value'),
            el.getAttribute('alt'),
        );
        for (const t of candidates) {
            if (t && t.trim().length > 0)
                return t.replace(/\\s+/g, ' ').trim().substring(0, 80);
        }
        return '';
    }

    function getRole(el) {
        const r = el.getAttribute('role');
        if (r) return r.toUpperCase();
        const t = el.tagName.toLowerCase();
        if (t === 'a') return 'LINK';
        if (t === 'button') return 'BUTTON';
        if (t === 'input') {
            const tp = (el.getAttribute('type') || 'text').toUpperCase();
            return ['TEXT','TEL','NUMBER','EMAIL','SEARCH'].includes(tp) ? 'INPUT' : tp;
        }
        if (t === 'select') return 'SELECT';
        return 'CLICK';
    }

    function tryAdd(el, role) {
        if (results.length >= 50) return;
        try {
            const style = window.getComputedStyle(el);
            if (!isVisible(style)) return;
            const rect = el.getBoundingClientRect();
            if (!inViewport(rect)) return;
            const text = getText(el);
            if (!text || text.length < 2) return;
            const key = text.toLowerCase().substring(0, 50);
            if (seen.has(key)) return;
            seen.add(key);
            results.push('[' + role + '] ' + text);
        } catch(e) {}
    }

    // ── Pass 1: semantic interactive elements ─────────────────────────────────
    const sem = [
        'a[href]', 'button:not([disabled])',
        'input:not([type="hidden"]):not([disabled])',
        'select:not([disabled])',
        '[role="button"]', '[role="link"]', '[role="tab"]',
        '[role="menuitem"]', '[role="option"]', '[role="searchbox"]',
        '[tabindex="0"]',
    ].join(', ');
    for (const el of document.querySelectorAll(sem)) {
        tryAdd(el, getRole(el));
    }

    // ── Pass 2: cursor:pointer scan — catches Angular/React product tiles, CTAs
    //   and any non-semantic element BFL uses as a clickable.
    //   Limited to 700 candidates to keep this fast.
    const nsq = [
        '[onclick]', '[ng-click]',
        '[data-href]', '[data-link]', '[data-url]', '[data-route]',
        '[class*="btn" i]', '[class*="cta" i]',
        '[class*="tile" i]', '[class*="card" i]',
        '[class*="product" i]', '[class*="category" i]',
        '[class*="item" i]', '[class*="nav-item" i]',
        '[class*="menu-item" i]', '[class*="link" i]',
        '[class*="action" i]', '[class*="apply" i]',
        'li', 'div[class]', 'span[class]',
    ].join(', ');
    let p2n = 0;
    for (const el of document.querySelectorAll(nsq)) {
        if (results.length >= 50) break;
        if (p2n++ > 700) break;
        try {
            const style = window.getComputedStyle(el);
            if (style.cursor !== 'pointer') continue;
            tryAdd(el, 'CLICK');
        } catch(e) {}
    }

    return results;
}
"""

_VISIBLE_TEXT_JS = """
() => {
    const vpH = window.innerHeight;
    const allTexts = [];
    const financialTexts = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    // Regex to spot financial values: percentages, rupee amounts, EMI figures, tenures
    const financialRe = /[\\u20b9%]|\\d+\\.\\d+|p\\.a\\.?|EMI|interest|tenure|month|year|lakh|crore/i;
    let node;
    while ((node = walker.nextNode())) {
        const el = node.parentElement;
        if (!el) continue;
        try {
            const rect  = el.getBoundingClientRect();
            if (rect.bottom <= 0 || rect.top >= vpH) continue;
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden') continue;
            const t = (node.textContent || '').replace(/\\s+/g, ' ').trim();
            if (t.length < 2) continue;
            allTexts.push(t);
            if (financialRe.test(t)) financialTexts.push(t);
        } catch(e) { continue; }
    }
    // Lead with financial values so they are never cut off by the character limit,
    // then append the rest of the visible text for context.
    const financial = financialTexts.join(' ');
    const rest = allTexts.filter(t => !financialTexts.includes(t)).join(' ');
    const combined = (financial + ' | ' + rest).replace(/\\s+/g, ' ').trim();
    return combined.substring(0, 1500);
}
"""

_SCROLL_INFO_JS = """
() => ({
    scrollTop: Math.round(window.scrollY || document.documentElement.scrollTop),
    pageHeight: Math.max(
        document.body.scrollHeight,
        document.documentElement.scrollHeight
    ),
    viewportHeight: window.innerHeight,
})
"""

_OVERLAY_JS = """
() => {
    // ── Search input state detection ──────────────────────────────────────────
    // Two distinct states:
    //   (A) Search bar just opened, input empty — this IS a full-screen overlay
    //       experience on BFL.  Report as overlay so the agent types a keyword.
    //   (B) Text has already been typed — the suggestion drawer is now showing.
    //       This is NOT an overlay.  The agent must pick a suggestion or tap the
    //       search icon.  Suppress overlay detection entirely in this state so
    //       the agent does not try to dismiss the suggestion drawer.
    const activeEl = document.activeElement;
    if (activeEl) {
        const t = activeEl.tagName.toLowerCase();
        if (t === 'input' || t === 'textarea') {
            const type = (activeEl.getAttribute('type')        || '').toLowerCase();
            const ph   = (activeEl.getAttribute('placeholder') || '').toLowerCase();
            const al   = (activeEl.getAttribute('aria-label')  || '').toLowerCase();
            const role = (activeEl.getAttribute('role')        || '').toLowerCase();
            const isSearch = type === 'search' || role === 'searchbox' ||
                             ph.includes('search') || al.includes('search');
            if (isSearch) {
                const currentValue = (activeEl.value || '').trim();
                if (!currentValue) {
                    // State A: blank focused search bar (full-screen search overlay)
                    const label = activeEl.getAttribute('placeholder') ||
                                  activeEl.getAttribute('aria-label') || 'search';
                    return {
                        has_overlay: true,
                        has_search_suggestions: false,
                        text: 'Search bar active: "' + label + '". Type your search keyword or dismiss_overlay to cancel.',
                    };
                }
                // State B: text typed, suggestion drawer is likely open.
                // Do NOT report as overlay — let the agent interact with suggestions.
                return {
                    has_overlay: false,
                    has_search_suggestions: true,
                    text: '',
                };
            }
        }
    }

    // ── Standard modal / popup overlay detection ──────────────────────────────
    const candidates = document.querySelectorAll(
        '[role="dialog"], [role="alertdialog"], ' +
        '.modal, .Modal, .popup, .Popup, .overlay, ' +
        '[class*="modal" i]:not([class*="modal-backdrop"]), ' +
        '[class*="popup" i], [class*="dialog" i], ' +
        '[id*="modal" i], [id*="popup" i]'
    );
    // Custom dropdowns / tenure selectors / pickers / tabs often reuse
    // modal/dialog-ish class names but are NOT blocking overlays — the agent
    // should interact with them, not try to dismiss them. (issue 6)
    const dropdownRe = /dropdown|drop-down|select|picker|tenure|accordion|\\btab\\b|tabs|tooltip|combobox|listbox|menu|suggest|autocomplete|slider|carousel|calendar|datepicker|chip|pill|popover|tippy/i;
    for (const el of candidates) {
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') continue;
        const rect = el.getBoundingClientRect();
        if (rect.width < 100 || rect.height < 50) continue;
        // Role-based exclusions: interactive controls, not blocking overlays.
        const role = (el.getAttribute('role') || '').toLowerCase();
        if (['listbox','option','menu','menuitem','combobox','tablist','tab','tabpanel'].includes(role)) continue;
        if (el.tagName === 'SELECT') continue;
        if (el.closest('[role="listbox"]') || el.closest('[role="combobox"]') || el.closest('[role="menu"]')) continue;
        // Class/id-based exclusion for custom dropdowns/pickers/tenure selectors.
        const cls = ((el.className && el.className.toString) ? el.className.toString() : '') + ' ' + (el.id || '');
        if (dropdownRe.test(cls)) continue;
        // A true blocking modal is overlay-positioned (fixed/absolute/sticky) OR
        // spans most of the screen width. Small anchored inline panels are not.
        const pos = style.position;
        const isOverlayPositioned = (pos === 'fixed' || pos === 'absolute' || pos === 'sticky');
        const coversWidth = rect.width >= window.innerWidth * 0.6;
        if (!isOverlayPositioned && !coversWidth) continue;
        const text = (el.innerText || '').replace(/\\s+/g, ' ').trim().substring(0, 300);
        return { has_overlay: true, has_search_suggestions: false, text: text };
    }
    return { has_overlay: false, has_search_suggestions: false, text: '' };
}
"""


async def extract_state(page) -> PageState:
    """Extract current page state from a Playwright page object."""
    url   = page.url
    title = await page.title()

    try:
        elements = await page.evaluate(_VIEWPORT_ELEMENTS_JS)
    except Exception:
        elements = []

    try:
        scroll_info = await page.evaluate(_SCROLL_INFO_JS)
        scroll_pos  = scroll_info.get("scrollTop", 0)
        page_height = scroll_info.get("pageHeight", 0)
        vp_height   = scroll_info.get("viewportHeight", 740)
        at_bottom   = (scroll_pos + vp_height + 20) >= page_height
    except Exception:
        scroll_pos = 0
        page_height = 0
        at_bottom = False

    try:
        overlay_info             = await page.evaluate(_OVERLAY_JS)
        has_overlay              = overlay_info.get("has_overlay", False)
        overlay_text             = overlay_info.get("text", "")
        search_suggestions_active = overlay_info.get("has_search_suggestions", False)
    except Exception:
        has_overlay              = False
        overlay_text             = ""
        search_suggestions_active = False

    try:
        visible_text = await page.evaluate(_VISIBLE_TEXT_JS)
    except Exception:
        visible_text = ""

    return PageState(
        url                      = url,
        title                    = title,
        viewport_elements        = elements,
        has_overlay              = has_overlay,
        overlay_text             = overlay_text,
        scroll_position          = scroll_pos,
        page_height              = page_height,
        at_bottom                = at_bottom,
        visible_text             = visible_text,
        search_suggestions_active = search_suggestions_active,
    )
