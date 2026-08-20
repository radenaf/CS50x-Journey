(function () {
    const siteData = window.SiteData || {};

    function slugify(value) {
        return String(value)
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/(^-|-$)/g, "");
    }

    function sectionHeading(options) {
        const eyebrow = options.eyebrow ? `<p class="section-eyebrow">${options.eyebrow}</p>` : "";
        const intro = options.intro ? `<p class="section-intro">${options.intro}</p>` : "";

        return `
            <div class="section-heading${options.centered ? " section-heading-centered" : ""}">
                ${eyebrow}
                <h2>${options.title}</h2>
                ${intro}
            </div>
        `;
    }

    function buttonLink(label, href, variant) {
        return `<a class="button ${variant === "secondary" ? "button-secondary" : "button-primary"}" href="${href}">${label}</a>`;
    }

    function headerNavigation(items) {
        return items
            .map((item) => {
                const hasChildren = Array.isArray(item.children) && item.children.length > 0;
                const submenuId = `${slugify(item.label)}-submenu`;

                if (!hasChildren) {
                    return `
                        <li class="nav-item">
                            <a href="${item.href}">${item.label}</a>
                        </li>
                    `;
                }

                return `
                    <li class="nav-item nav-item-has-children">
                        <div class="nav-parent">
                            <a href="${item.href}">${item.label}</a>
                            <button class="submenu-toggle" type="button" aria-expanded="false" aria-controls="${submenuId}">
                                <span class="visually-hidden">Toggle ${item.label} submenu</span>
                                <span aria-hidden="true">+</span>
                            </button>
                        </div>
                        <ul id="${submenuId}" class="nav-submenu">
                            ${item.children
                                .map(
                                    (child) => `
                                        <li><a href="${child.href}">${child.label}</a></li>
                                    `
                                )
                                .join("")}
                        </ul>
                    </li>
                `;
            })
            .join("");
    }

    function footerLinkList(items) {
        return items.map((item) => `<li><a href="${item.href}">${item.label}</a></li>`).join("");
    }

    function renderHeader(currentPage) {
        const site = siteData.site;
        const items = siteData.navigation || [];

        return `
            <header class="site-header">
                <div class="header-shell container">
                    <a class="site-brand" href="index.html" aria-label="${site.fullName}">
                        <span class="brand-logos" aria-hidden="true">
                            <span class="logo-placeholder">[IMR LOGO PLACEHOLDER]</span>
                            <span class="logo-placeholder">[NIH LOGO PLACEHOLDER]</span>
                        </span>
                        <span class="brand-copy">
                            <span class="brand-title">${site.fullName}</span>
                            <span class="brand-meta">${site.department} · ${site.institute} · ${site.umbrella}</span>
                        </span>
                    </a>
                    <div class="header-actions">
                        <button class="search-toggle" type="button" aria-expanded="false" aria-controls="site-search-panel">Search</button>
                        <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-navigation">
                            <span class="visually-hidden">Toggle navigation</span>
                            <span aria-hidden="true"></span>
                        </button>
                    </div>
                </div>
                <div id="site-search-panel" class="site-search-panel" hidden>
                    <div class="container search-panel-inner">
                        <label class="search-label" for="site-search-input">Search the site</label>
                        <input id="site-search-input" type="search" placeholder="Search pages, tests, resources, and publications" autocomplete="off">
                        <div id="site-search-results" class="search-results" aria-live="polite"></div>
                    </div>
                </div>
                <nav id="site-navigation" class="site-navigation" aria-label="Primary">
                    <div class="container">
                        <ul class="nav-list" data-current-page="${currentPage}">
                            ${headerNavigation(items)}
                        </ul>
                    </div>
                </nav>
            </header>
        `;
    }

    function renderFooter() {
        const site = siteData.site;

        return `
            <footer class="site-footer">
                <div class="container footer-grid">
                    <div>
                        <p class="footer-kicker">Rickettsial Laboratory</p>
                        <h2>${site.department}</h2>
                        <p>${site.institute}</p>
                        <p>${site.umbrella}</p>
                    </div>
                    <div>
                        <h3>Site Links</h3>
                        <ul class="footer-links">
                            ${footerLinkList(siteData.navigation || [])}
                        </ul>
                    </div>
                    <div>
                        <h3>Institutional Links</h3>
                        <ul class="footer-links">
                            ${(site.institutionalLinks || [])
                                .map(
                                    (link) => `
                                        <li><a href="${link.href}">${link.placeholder}</a></li>
                                    `
                                )
                                .join("")}
                        </ul>
                    </div>
                    <div>
                        <h3>Contact</h3>
                        <p>${site.address}</p>
                        <p>${site.phone}</p>
                        <p>${site.email}</p>
                    </div>
                </div>
                <div class="container footer-bottom">
                    <p>Privacy</p>
                    <p>Accessibility</p>
                    <p>Copyright © <span id="site-year"></span> Rickettsial Laboratory</p>
                </div>
            </footer>
        `;
    }

    function renderBreadcrumbs(items) {
        if (!items || !items.length) {
            return "";
        }

        return `
            <nav class="breadcrumbs" aria-label="Breadcrumb">
                <ol>
                    ${items
                        .map((item, index) => {
                            const isLast = index === items.length - 1;
                            return `
                                <li>
                                    ${isLast ? `<span aria-current="page">${item.label}</span>` : `<a href="${item.href}">${item.label}</a>`}
                                </li>
                            `;
                        })
                        .join("")}
                </ol>
            </nav>
        `;
    }

    function renderOverviewCards(items) {
        return items
            .map(
                (item) => `
                    <article class="content-card">
                        <h3>${item.title}</h3>
                        <p>${item.description}</p>
                        <a class="text-link" href="${item.href}">${item.cta}</a>
                    </article>
                `
            )
            .join("");
    }

    function renderDiagnosticCards(items, detailed) {
        return items
            .map(
                (item) => `
                    <article class="content-card diagnostic-card">
                        <div class="card-header-row">
                            <div>
                                <p class="card-eyebrow">Diagnostic Test</p>
                                <h3>${item.name}</h3>
                            </div>
                            <span class="badge">${item.pathogen}</span>
                        </div>
                        <p>${item.purpose}</p>
                        <dl class="definition-grid${detailed ? " definition-grid-detailed" : ""}">
                            <div><dt>Method</dt><dd>${item.method}</dd></div>
                            <div><dt>Specimen Type</dt><dd>${item.specimenType}</dd></div>
                            <div><dt>Collection</dt><dd>${item.collectionInstructions}</dd></div>
                            <div><dt>Container</dt><dd>${item.container}</dd></div>
                            <div><dt>Storage</dt><dd>${item.storage}</dd></div>
                            <div><dt>Transport</dt><dd>${item.transport}</dd></div>
                            <div><dt>Turnaround Time</dt><dd>${item.turnaroundTime}</dd></div>
                            <div><dt>Result Format</dt><dd>${item.resultFormat}</dd></div>
                            <div><dt>Interpretation</dt><dd>${item.interpretation}</dd></div>
                            <div><dt>Limitations</dt><dd>${item.limitations}</dd></div>
                            <div><dt>Request Form</dt><dd>${item.requestForm}</dd></div>
                            <div><dt>Additional Notes</dt><dd>${item.notes}</dd></div>
                        </dl>
                    </article>
                `
            )
            .join("");
    }

    function renderResearchCards(items) {
        return items
            .map(
                (item) => `
                    <article class="content-card research-card">
                        <p class="card-eyebrow">Current Project</p>
                        <h3>${item.title}</h3>
                        <p>${item.description}</p>
                        <dl class="definition-grid">
                            <div><dt>Objectives</dt><dd>${item.objectives}</dd></div>
                            <div><dt>Pathogens</dt><dd>${item.pathogens}</dd></div>
                            <div><dt>Methods</dt><dd>${item.methods}</dd></div>
                            <div><dt>Collaborators</dt><dd>${item.collaborators}</dd></div>
                            <div><dt>Status</dt><dd>${item.status}</dd></div>
                            <div><dt>Publications</dt><dd>${item.publications}</dd></div>
                        </dl>
                    </article>
                `
            )
            .join("");
    }

    function renderStaffCards(items) {
        return items
            .map(
                (item) => `
                    <article class="content-card staff-card">
                        <img src="${item.photo}" alt="Placeholder portrait for staff profile" loading="lazy">
                        <div class="staff-copy">
                            <h3>${item.name}</h3>
                            <p class="staff-position">${item.position}</p>
                            <dl class="definition-grid">
                                <div><dt>Qualifications</dt><dd>${item.qualifications}</dd></div>
                                <div><dt>Role</dt><dd>${item.role}</dd></div>
                                <div><dt>Research Interests</dt><dd>${item.researchInterests}</dd></div>
                                <div><dt>Email</dt><dd>${item.email}</dd></div>
                                <div><dt>ORCID</dt><dd>${item.orcid}</dd></div>
                                <div><dt>Publications</dt><dd>${item.publications}</dd></div>
                            </dl>
                        </div>
                    </article>
                `
            )
            .join("");
    }

    function renderPublicationCards(items) {
        if (!items.length) {
            return `<div class="empty-state"><p>No publications match the current filters.</p></div>`;
        }

        return items
            .map(
                (item) => `
                    <article class="content-card publication-card">
                        <div class="card-header-row">
                            <div>
                                <p class="card-eyebrow">Publication</p>
                                <h3>${item.title}</h3>
                            </div>
                            <span class="badge">${item.year}</span>
                        </div>
                        <p class="publication-meta">${item.authors}</p>
                        <p class="publication-meta">${item.journal}</p>
                        <dl class="definition-grid">
                            <div><dt>Research Area</dt><dd>${item.researchArea}</dd></div>
                            <div><dt>Pathogen</dt><dd>${item.pathogen}</dd></div>
                            <div><dt>DOI</dt><dd>${item.doi}</dd></div>
                            <div><dt>PMID</dt><dd>${item.pmid}</dd></div>
                        </dl>
                        <p>${item.abstract}</p>
                        <a class="text-link" href="${item.url}">External publication URL</a>
                    </article>
                `
            )
            .join("");
    }

    function renderResourceCards(items) {
        return items
            .map(
                (item) => `
                    <article class="content-card resource-card">
                        <div class="card-header-row">
                            <div>
                                <p class="card-eyebrow">${item.category}</p>
                                <h3>${item.title}</h3>
                            </div>
                            <span class="badge">${item.type}</span>
                        </div>
                        <p>${item.description}</p>
                        <dl class="definition-grid compact-grid">
                            <div><dt>Date Updated</dt><dd>${item.dateUpdated}</dd></div>
                            <div><dt>Link</dt><dd><a class="text-link" href="${item.href}">Open resource</a></dd></div>
                        </dl>
                    </article>
                `
            )
            .join("");
    }

    function renderNewsCards(items) {
        return items
            .map(
                (item) => `
                    <article class="content-card news-card">
                        <img src="${item.image}" alt="Placeholder image for news item" loading="lazy">
                        <div class="news-copy">
                            <p class="card-eyebrow">${item.category}</p>
                            <h3>${item.title}</h3>
                            <p class="news-date">${item.date}</p>
                            <p>${item.summary}</p>
                            <div class="article-body">
                                <p>${item.content}</p>
                            </div>
                        </div>
                    </article>
                `
            )
            .join("");
    }

    function renderRequestForms(items) {
        return items
            .map(
                (item) => `
                    <article class="content-card form-card">
                        <h3>${item.title}</h3>
                        <p>${item.description}</p>
                        <a class="button button-secondary" href="${item.href}" download>${item.fileLabel}</a>
                    </article>
                `
            )
            .join("");
    }

    function renderFaqs(items) {
        return items
            .map(
                (item) => `
                    <details class="faq-item">
                        <summary>${item.question}</summary>
                        <p>${item.answer}</p>
                    </details>
                `
            )
            .join("");
    }

    window.SiteComponents = {
        buttonLink,
        renderBreadcrumbs,
        renderDiagnosticCards,
        renderFooter,
        renderHeader,
        renderFaqs,
        renderNewsCards,
        renderOverviewCards,
        renderPublicationCards,
        renderRequestForms,
        renderResearchCards,
        renderResourceCards,
        renderSectionHeading: sectionHeading,
        renderStaffCards,
        slugify
    };
})();
