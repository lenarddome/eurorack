document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('aside .terminal-mkdocs-side-nav-li').forEach(function (li) {
        const ul = li.querySelector(':scope > ul.terminal-mkdocs-side-nav-li-ul');
        if (!ul) return;
        const label = li.querySelector(':scope > a, :scope > span');
        if (!label) return;

        const toggle = document.createElement('span');
        toggle.className = 'terminal-mkdocs-side-nav-toggle';
        toggle.setAttribute('role', 'button');
        toggle.setAttribute('aria-label', 'Toggle section');
        toggle.tabIndex = 0;

        function doToggle(e) {
            e.preventDefault();
            e.stopPropagation();
            li.classList.toggle('collapsed');
        }
        toggle.addEventListener('click', doToggle);
        toggle.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') doToggle(e);
        });

        label.parentNode.insertBefore(toggle, label);
    });
});
