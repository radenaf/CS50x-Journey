document.addEventListener("DOMContentLoaded", () => {
    const siteData = window.SiteData;
    const components = window.SiteComponents;

    if (!siteData || !components) {
        return;
    }

    const currentPage = document.body.dataset.page || "";

    injectShell(currentPage);
    applySiteFields(siteData.site);
    markActiveNavigation(currentPage);
    initializeGlobalInteractions();
    initializePage(currentPage, siteData, components);
});

function injectShell(currentPage) {
    const headerNode = document.querySelector("[data-site-header]");
    const footerNode = document.querySelector("[data-site-footer]");
    const breadcrumbNode = document.querySelector("[data-breadcrumbs]");

    if (headerNode) {
        headerNode.innerHTML = window.SiteComponents.renderHeader(currentPage);
    }

    if (footerNode) {
        footerNode.innerHTML = window.SiteComponents.renderFooter();
    }

    if (breadcrumbNode) {
        const breadcrumbItems = JSON.parse(breadcrumbNode.dataset.breadcrumbs || "[]");
        breadcrumbNode.innerHTML = window.SiteComponents.renderBreadcrumbs(breadcrumbItems);
    }

    const yearNode = document.getElementById("site-year");
    if (yearNode) {
        yearNode.textContent = new Date().getFullYear();
    }
}

function applySiteFields(site) {
    document.querySelectorAll("[data-site-field]").forEach((node) => {
        const key = node.dataset.siteField;
        if (site[key]) {
            node.textContent = site[key];
        }
    });
}

function markActiveNavigation(currentPage) {
    const nav = document.querySelector(".nav-list");
    if (!nav) {
        return;
    }

    nav.querySelectorAll("a").forEach((link) => {
        const href = link.getAttribute("href");
        if (!href) {
            return;
        }

        const normalized = href.split("#")[0];
        if (normalized === currentPage || (currentPage === "index.html" && normalized === "index.html")) {
            link.setAttribute("aria-current", "page");
        }
    });
}

function initializeGlobalInteractions() {
    const navToggle = document.querySelector(".nav-toggle");
    const navigation = document.getElementById("site-navigation");
    const searchToggle = document.querySelector(".search-toggle");
    const searchPanel = document.getElementById("site-search-panel");
    const searchInput = document.getElementById("site-search-input");
    const searchResults = document.getElementById("site-search-results");
    const feedback = document.getElementById("contact-form-feedback");
    const contactForm = document.getElementById("contact-form");

    if (navToggle && navigation) {
        navToggle.addEventListener("click", () => {
            const isOpen = navToggle.getAttribute("aria-expanded") === "true";
            navToggle.setAttribute("aria-expanded", String(!isOpen));
            navigation.classList.toggle("site-navigation-open", !isOpen);
        });
    }

    document.querySelectorAll(".submenu-toggle").forEach((button) => {
        button.addEventListener("click", () => {
            const parent = button.closest(".nav-item-has-children");
            const isOpen = button.getAttribute("aria-expanded") === "true";
            button.setAttribute("aria-expanded", String(!isOpen));
            if (parent) {
                parent.classList.toggle("submenu-open", !isOpen);
            }
        });
    });

    if (searchToggle && searchPanel && searchInput && searchResults) {
        const searchIndex = buildSearchIndex();
        searchToggle.addEventListener("click", () => {
            const isOpen = searchToggle.getAttribute("aria-expanded") === "true";
            searchToggle.setAttribute("aria-expanded", String(!isOpen));
            searchPanel.hidden = isOpen;
            if (!isOpen) {
                searchInput.focus();
                renderSearchResults(searchIndex, "", searchResults);
            }
        });

        searchInput.addEventListener("input", (event) => {
            renderSearchResults(searchIndex, event.target.value, searchResults);
        });
    }

    if (contactForm && feedback) {
        contactForm.addEventListener("submit", (event) => {
            event.preventDefault();
            feedback.textContent = "This form is a front-end placeholder only. No email has been sent.";
            contactForm.reset();
        });
    }
}

function buildSearchIndex() {
    const data = window.SiteData;
    const navigationItems = (data.navigation || []).flatMap((item) => {
        const entries = [{ title: item.label, href: item.href, category: "Page" }];
        if (item.children) {
            item.children.forEach((child) => {
                entries.push({ title: child.label, href: child.href, category: item.label });
            });
        }
        return entries;
    });

    const testItems = (data.diagnosticTests || []).map((item) => ({
        title: item.name,
        href: "rickettsial-testing.html",
        category: "Diagnostic Test",
        keywords: `${item.pathogen} ${item.method} ${item.specimenType}`
    }));

    const publicationItems = (data.publications || []).map((item) => ({
        title: item.title,
        href: "publications.html",
        category: "Publication",
        keywords: `${item.authors} ${item.researchArea} ${item.pathogen}`
    }));

    const resourceItems = (data.resources || []).map((item) => ({
        title: item.title,
        href: "resources.html",
        category: item.category,
        keywords: `${item.description} ${item.type}`
    }));

    const newsItems = (data.news || []).map((item) => ({
        title: item.title,
        href: "news.html",
        category: "News",
        keywords: `${item.summary} ${item.category}`
    }));

    return [...navigationItems, ...testItems, ...publicationItems, ...resourceItems, ...newsItems];
}

function renderSearchResults(items, query, target) {
    const value = query.trim().toLowerCase();
    const filtered = value
        ? items.filter((item) => `${item.title} ${item.category} ${item.keywords || ""}`.toLowerCase().includes(value))
        : items.slice(0, 8);

    target.innerHTML = filtered.length
        ? `<ul>${filtered
              .slice(0, 8)
              .map(
                  (item) => `
                    <li>
                        <a href="${item.href}">
                            <strong>${item.title}</strong>
                            <span>${item.category}</span>
                        </a>
                    </li>
                `
              )
              .join("")}</ul>`
        : `<p class="search-empty">No matching content found.</p>`;
}

function initializePage(currentPage, siteData, components) {
    const initializers = {
        "index.html": initializeHomePage,
        "about.html": initializeAboutPage,
        "team.html": initializeTeamPage,
        "diagnostic-services.html": initializeDiagnosticServicesPage,
        "rickettsial-testing.html": initializeTestingPage,
        "specimen-submission.html": initializeSpecimenSubmissionPage,
        "test-information.html": initializeTestInformationPage,
        "request-forms.html": initializeRequestFormsPage,
        "research.html": initializeResearchPage,
        "publications.html": initializePublicationsPage,
        "resources.html": initializeResourcesPage,
        "news.html": initializeNewsPage,
        "contact.html": initializeContactPage
    };

    const initializer = initializers[currentPage];
    if (initializer) {
        initializer(siteData, components);
    }
}

function initializeHomePage(siteData, components) {
    const homeSections = document.querySelector("[data-home-sections]");
    const featuredPublications = document.querySelector("[data-featured-publications]");
    const featuredNews = document.querySelector("[data-featured-news]");
    const resourceHighlights = document.querySelector("[data-resource-highlights]");

    if (homeSections) {
        homeSections.innerHTML = components.renderOverviewCards(siteData.homepageSections);
    }
    if (featuredPublications) {
        featuredPublications.innerHTML = components.renderPublicationCards(siteData.publications.slice(0, 2));
    }
    if (featuredNews) {
        featuredNews.innerHTML = components.renderNewsCards(siteData.news.slice(0, 2));
    }
    if (resourceHighlights) {
        resourceHighlights.innerHTML = components.renderResourceCards(siteData.resources.slice(0, 3));
    }
}

function initializeAboutPage(siteData, components) {
    const quickLinks = document.querySelector("[data-about-links]");
    if (quickLinks) {
        quickLinks.innerHTML = components.renderOverviewCards([
            { title: "Our Team", description: "[TEAM OVERVIEW]", href: "team.html", cta: "Meet the Team" },
            { title: "Diagnostic Services", description: "[DIAGNOSTIC ROLE OVERVIEW]", href: "diagnostic-services.html", cta: "Access Services" },
            { title: "Research", description: "[RESEARCH ROLE OVERVIEW]", href: "research.html", cta: "View Research" }
        ]);
    }
}

function initializeTeamPage(siteData, components) {
    const teamGrid = document.querySelector("[data-team-grid]");
    if (teamGrid) {
        teamGrid.innerHTML = components.renderStaffCards(siteData.staff);
    }
}

function initializeDiagnosticServicesPage(siteData, components) {
    const servicesGrid = document.querySelector("[data-services-grid]");
    const formsGrid = document.querySelector("[data-forms-grid]");
    if (servicesGrid) {
        servicesGrid.innerHTML = components.renderOverviewCards([
            { title: "Rickettsial Testing", description: "[RICKETTSIAL TESTING OVERVIEW]", href: "rickettsial-testing.html", cta: "View Testing" },
            { title: "Specimen Submission", description: "[SPECIMEN SUBMISSION OVERVIEW]", href: "specimen-submission.html", cta: "Submission Guidance" },
            { title: "Test Information", description: "[TEST INFORMATION OVERVIEW]", href: "test-information.html", cta: "Open Test Information" }
        ]);
    }
    if (formsGrid) {
        formsGrid.innerHTML = components.renderRequestForms(siteData.requestForms);
    }
}

function initializeTestingPage(siteData, components) {
    const testGrid = document.querySelector("[data-diagnostic-tests]");
    if (testGrid) {
        testGrid.innerHTML = components.renderDiagnosticCards(siteData.diagnosticTests, true);
    }
}

function initializeSpecimenSubmissionPage(siteData, components) {
    const formsGrid = document.querySelector("[data-request-form-links]");
    if (formsGrid) {
        formsGrid.innerHTML = components.renderRequestForms(siteData.requestForms);
    }
}

function initializeTestInformationPage(siteData, components) {
    const informationGrid = document.querySelector("[data-test-information]");
    if (informationGrid) {
        informationGrid.innerHTML = components.renderDiagnosticCards(siteData.diagnosticTests, false);
    }
}

function initializeRequestFormsPage(siteData, components) {
    const requestForms = document.querySelector("[data-request-forms]");
    if (requestForms) {
        requestForms.innerHTML = components.renderRequestForms(siteData.requestForms);
    }
}

function initializeResearchPage(siteData, components) {
    const currentProjects = document.querySelector("[data-research-projects]");
    if (currentProjects) {
        currentProjects.innerHTML = components.renderResearchCards(siteData.researchProjects);
    }
}

function initializePublicationsPage(siteData, components) {
    const search = document.getElementById("publication-search");
    const year = document.getElementById("publication-year");
    const area = document.getElementById("publication-area");
    const pathogen = document.getElementById("publication-pathogen");
    const sort = document.getElementById("publication-sort");
    const results = document.getElementById("publication-results");

    if (!(search && year && area && pathogen && sort && results)) {
        return;
    }

    fillSelect(year, ["All years", ...uniqueValues(siteData.publications, "year")]);
    fillSelect(area, ["All research areas", ...uniqueValues(siteData.publications, "researchArea")]);
    fillSelect(pathogen, ["All pathogens", ...uniqueValues(siteData.publications, "pathogen")]);

    const render = () => {
        let items = [...siteData.publications];
        const keyword = search.value.trim().toLowerCase();
        const yearValue = year.value;
        const areaValue = area.value;
        const pathogenValue = pathogen.value;
        const sortValue = sort.value;

        if (keyword) {
            items = items.filter((item) => `${item.title} ${item.authors} ${item.abstract}`.toLowerCase().includes(keyword));
        }
        if (yearValue !== "All years") {
            items = items.filter((item) => item.year === yearValue);
        }
        if (areaValue !== "All research areas") {
            items = items.filter((item) => item.researchArea === areaValue);
        }
        if (pathogenValue !== "All pathogens") {
            items = items.filter((item) => item.pathogen === pathogenValue);
        }

        items.sort((left, right) => {
            const leftYear = parseInt(left.year, 10);
            const rightYear = parseInt(right.year, 10);
            if (Number.isNaN(leftYear) || Number.isNaN(rightYear)) {
                return sortValue === "oldest" ? String(left.year).localeCompare(String(right.year)) : String(right.year).localeCompare(String(left.year));
            }
            return sortValue === "oldest" ? leftYear - rightYear : rightYear - leftYear;
        });

        results.innerHTML = components.renderPublicationCards(items);
    };

    [search, year, area, pathogen, sort].forEach((control) => control.addEventListener("input", render));
    [year, area, pathogen, sort].forEach((control) => control.addEventListener("change", render));
    render();
}

function initializeResourcesPage(siteData, components) {
    const categories = document.querySelector("[data-resource-groups]");
    const faqGrid = document.querySelector("[data-faqs]");
    if (categories) {
        categories.innerHTML = components.renderResourceCards(siteData.resources);
    }
    if (faqGrid) {
        faqGrid.innerHTML = components.renderFaqs(siteData.faqs);
    }
}

function initializeNewsPage(siteData, components) {
    const newsGrid = document.querySelector("[data-news-grid]");
    if (newsGrid) {
        newsGrid.innerHTML = components.renderNewsCards(siteData.news);
    }
}

function initializeContactPage(siteData, components) {
    const diagnosticContacts = document.querySelector("[data-contact-cards]");
    if (diagnosticContacts) {
        diagnosticContacts.innerHTML = components.renderOverviewCards([
            { title: "Diagnostic Enquiries", description: "[DIAGNOSTIC ENQUIRY CONTACT DETAILS]", href: "#contact-form-section", cta: "Send Enquiry" },
            { title: "Research Enquiries", description: "[RESEARCH ENQUIRY CONTACT DETAILS]", href: "#contact-form-section", cta: "Send Enquiry" },
            { title: "General Enquiries", description: "[GENERAL ENQUIRY CONTACT DETAILS]", href: "#contact-form-section", cta: "Send Enquiry" }
        ]);
    }
}

function uniqueValues(items, key) {
    return [...new Set(items.map((item) => item[key]))];
}

function fillSelect(select, values) {
    select.innerHTML = values.map((value) => `<option value="${value}">${value}</option>`).join("");
}
