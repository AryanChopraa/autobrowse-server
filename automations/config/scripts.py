HIGHLIGHT_LINKS_SCRIPT = """
(function() {
    // Remove existing gpt-link-text attributes
    document.querySelectorAll('[gpt-link-text]').forEach(e => {
        e.removeAttribute("gpt-link-text");
    });

    // Select all elements that can be clickable
    const elements = document.querySelectorAll(
        "a, button, input, textarea, [role=button], [role=treeitem]"
    );

    elements.forEach(e => {
        function isElementVisible(el) {
            if (!el) return false; // Element does not exist

            function isStyleVisible(el) {
                const style = window.getComputedStyle(el);
                return style.width !== '0' &&
                    style.height !== '0' &&
                    style.opacity !== '0' &&
                    style.display !== 'none' &&
                    style.visibility !== 'hidden';
            }

            function isElementInViewport(el) {
                const rect = el.getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
            }

            // Check if the element is visible style-wise
            if (!isStyleVisible(el)) {
                return false;
            }

            // Traverse up the DOM and check if any ancestor element is hidden
            let parent = el;
            while (parent) {
                if (!isStyleVisible(parent)) {
                    return false;
                }
                parent = parent.parentElement;
            }

            // Finally, check if the element is within the viewport
            return isElementInViewport(el);
        }

        const position = e.getBoundingClientRect();

        if (position.width > 5 && position.height > 5 && isElementVisible(e)) {
            const link_text = e.textContent.replace(/[^a-zA-Z0-9 ]/g, '');
            e.setAttribute("gpt-link-text", link_text);
        }
    });
})();
"""

