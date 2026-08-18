const focusAutoFocusElement = () => {
    const focusableElements = [...document.querySelectorAll('[data-auto-focus]')];
    const hashTarget = window.location.hash ? document.querySelector(window.location.hash) : null;
    const targetElement = hashTarget?.querySelector('[data-auto-focus]') || focusableElements[0];
    targetElement?.focus();
};

document.addEventListener('DOMContentLoaded', focusAutoFocusElement);
window.addEventListener('pageshow', focusAutoFocusElement);
