// Search and filters for the Workflow Examples gallery.
// The markup is rendered by extensions/rapids_examples.py, cards arrive in recommendation order.
document.addEventListener("DOMContentLoaded", () => {
  const gallery = document.getElementById("examples-gallery");
  if (!gallery) return;

  const FACETS = {
    platform: "Platform",
    task: "Task",
    library: "Library",
    scale: "Scale",
    dataset: "Dataset",
    format: "Format",
    storage: "Storage",
  };
  const SUGGESTIONS = 8;
  const facets = Object.keys(FACETS);
  const aliases = JSON.parse(gallery.dataset.aliases);
  const cards = [...gallery.querySelectorAll(".eg-card")];
  const search = gallery.querySelector("#eg-search");
  const menus = [...gallery.querySelectorAll(".eg-facet")];
  const platformMenu = gallery.querySelector(
    '.eg-facet[data-facets="platform"]',
  );
  const buttons = [...gallery.querySelectorAll(".eg-platform[data-value]")];
  const services = gallery.querySelector(".eg-services");
  const chips = gallery.querySelector(".eg-chips");
  const count = gallery.querySelector(".eg-count");
  const empty = gallery.querySelector(".eg-empty");
  const siteSearch = gallery.querySelector(".eg-site-search");
  const siteSearchBase = siteSearch.getAttribute("href");
  const grid = gallery.querySelector(".eg-grid");
  const suggestions = gallery.querySelector("#eg-suggestions");
  // Topics are separated by "|" because they can contain spaces
  const topicsOf = (card) => card.dataset.topics.split("|").filter(Boolean);
  const topics = [...new Set(cards.flatMap(topicsOf))];
  const divider = document.createElement("p");
  divider.className = "eg-divider";
  divider.textContent = "Also mentioned in";

  // Notebooks whose text contains a word, looked up in the full-text index that
  // Sphinx loads on every page (searchindex.js). Words in a page's headings are
  // only in titleterms. Terms are stored stemmed, so other forms of the word are
  // the terms starting with its stem: "finance" is "financ", "financial" is "financi".
  // Without the index, search falls back to the cards alone.
  function notebooksMentioning(word) {
    const index = typeof Search !== "undefined" && Search._index;
    if (!index || typeof Stemmer === "undefined") return new Set();
    const stem = new Stemmer().stemWord(word);
    const found = new Set();
    for (const table of [index.terms, index.titleterms]) {
      for (const [term, pages] of Object.entries(table)) {
        if (
          term === stem ||
          (word.length > 2 && (term.startsWith(stem) || term.includes(word)))
        ) {
          [].concat(pages).forEach((page) => found.add(index.docnames[page]));
        }
      }
    }
    return found;
  }

  const boxes = (facet) => [
    ...gallery.querySelectorAll(`[data-facet="${facet}"] input`),
  ];
  const box = (facet, value) =>
    boxes(facet).find((input) => input.value === value);
  const selected = (facet) =>
    boxes(facet)
      .filter((input) => input.checked)
      .map((input) => input.value);
  const label = (facet, value) =>
    box(facet, value).parentElement.querySelector(".eg-option-label")
      .textContent;
  const values = (card, facet) => card.dataset[facet].split(" ");
  // The provider group (e.g. AWS) a platform belongs to, as its dropdown <div class="eg-group">
  const group = (value) => box("platform", value).closest(".eg-group");
  const groupValue = (value) =>
    group(value).querySelector(".eg-option--group input").value;

  const selectOnlyPlatform = (value) => {
    boxes("platform").forEach(
      (input) => (input.checked = input.value === value),
    );
    update();
  };

  function update() {
    const state = Object.fromEntries(
      facets.map((facet) => [facet, selected(facet)]),
    );
    const words = search.value.toLowerCase().split(/\s+/).filter(Boolean);
    const mentions = words.map(notebooksMentioning);
    const onCard = (card) =>
      words.every((word) => card.dataset.search.includes(word));
    const matches = (card, skip) =>
      words.every(
        (word, i) =>
          card.dataset.search.includes(word) ||
          mentions[i].has(card.dataset.docname),
      ) &&
      facets.every(
        (facet) =>
          facet === skip ||
          !state[facet].length ||
          state[facet].some((value) => values(card, facet).includes(value)),
      );

    // Cards whose metadata matches the search first, then a divider and the cards
    // that only mention it in the notebook, each group in recommendation order
    const about = cards.filter((card) => matches(card) && onCard(card));
    const mentioning = cards.filter((card) => matches(card) && !onCard(card));
    cards.forEach(
      (card) =>
        (card.hidden = !about.includes(card) && !mentioning.includes(card)),
    );
    divider.hidden = !about.length || !mentioning.length;
    grid.append(
      ...about,
      divider,
      ...mentioning,
      ...cards.filter((card) => card.hidden),
    );
    const shown = about.length + mentioning.length;

    // Counts per option, as if that option were added to the other filters
    facets.forEach((facet) =>
      boxes(facet).forEach((input) => {
        const n = cards.filter(
          (card) =>
            matches(card, facet) && values(card, facet).includes(input.value),
        ).length;
        input.parentElement.querySelector(".eg-n").textContent = n;
        input.disabled = n === 0 && !input.checked;
      }),
    );
    menus.forEach((menu) => {
      // "More filters" holds several facets
      const n = menu.dataset.facets
        .split(" ")
        .reduce((sum, facet) => sum + state[facet].length, 0);
      menu.querySelector(".eg-selected").textContent = n ? ` · ${n}` : "";
    });

    // Platform buttons stay pressed while one of their services is picked
    const only = state.platform.length === 1 ? state.platform[0] : null;
    buttons.forEach((button) => {
      const value = button.dataset.value;
      button.setAttribute(
        "aria-pressed",
        state.platform.includes(value) ||
          (only !== null && groupValue(only) === value),
      );
      button.disabled = box("platform", value).disabled;
    });
    renderServices(only);
    renderChips(state, words);

    count.textContent = `${shown} ${shown === 1 ? "example" : "examples"}`;
    empty.hidden = shown > 0;
    siteSearch.href = words.length
      ? `${siteSearchBase}?q=${encodeURIComponent(search.value.trim())}`
      : siteSearchBase;
    writeUrl(state);
  }

  // A second row with the services of the picked provider, e.g. AWS: EC2, SageMaker, EKS
  function renderServices(only) {
    // Rebuilding the row drops keyboard focus, so put it back on the same service
    const focused = services.contains(document.activeElement)
      ? document.activeElement.dataset.service
      : null;
    services.replaceChildren();
    const children = only
      ? [...group(only).querySelectorAll(".eg-option--child input")]
      : [];
    services.hidden = children.length === 0;
    children.forEach((input) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "eg-platform";
      button.dataset.service = input.value;
      button.textContent = label("platform", input.value);
      button.disabled = input.disabled;
      button.setAttribute("aria-pressed", input.checked);
      // Clicking the picked service again goes back to the whole provider
      button.addEventListener("click", () =>
        selectOnlyPlatform(input.checked ? groupValue(only) : input.value),
      );
      services.append(button);
      if (input.value === focused) button.focus();
    });
  }

  function renderChips(state, words) {
    chips.replaceChildren();
    facets.forEach((facet) =>
      state[facet].forEach((value) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "eg-chip";
        chip.textContent = `${FACETS[facet]}: ${label(facet, value)}`;
        chip.setAttribute("aria-label", `Remove filter ${chip.textContent}`);
        chip.addEventListener("click", () => {
          box(facet, value).checked = false;
          update();
        });
        chips.append(chip);
      }),
    );
    if (chips.children.length) {
      const clear = document.createElement("button");
      clear.type = "button";
      clear.className = "eg-clear";
      clear.textContent = "Clear all";
      clear.addEventListener("click", clearAll);
      chips.append(clear);
    }
    chips.hidden = chips.children.length === 0;
  }

  function clearAll() {
    facets.forEach((facet) =>
      boxes(facet).forEach((input) => (input.checked = false)),
    );
    search.value = "";
    update();
  }

  function writeUrl(state) {
    const params = new URLSearchParams(window.location.search);
    ["search", "filters", ...facets].forEach((key) => params.delete(key));
    facets.forEach(
      (facet) =>
        state[facet].length && params.set(facet, state[facet].join(",")),
    );
    if (search.value.trim()) params.set("search", search.value.trim());
    const query = params
      .toString()
      .replaceAll("%2F", "/")
      .replaceAll("%2C", ",");
    window.history.replaceState(
      null,
      "",
      query ? `?${query}` : window.location.pathname,
    );
  }

  // Suggestions under the search box: filter values, topics and example titles
  // containing what was typed. Picking a filter value applies it, a topic searches
  // for it and an example title opens that example.
  function suggestionsFor(typed) {
    const items = facets.flatMap((facet) =>
      boxes(facet)
        .filter((input) => !input.checked && !input.disabled)
        .map((input) => ({
          kind: FACETS[facet],
          text: label(facet, input.value),
          count: input.parentElement.querySelector(".eg-n").textContent,
          pick: () => {
            input.checked = true;
            search.value = "";
          },
        })),
    );
    topics.forEach((topic) =>
      items.push({
        kind: "Topic",
        text: topic,
        count: cards.filter((card) => topicsOf(card).includes(topic)).length,
        pick: () => (search.value = topic),
      }),
    );
    cards.forEach((card) => {
      const link = card.querySelector(".eg-card-title a");
      items.push({ kind: "Example", text: link.textContent, href: link.href });
    });
    // Names starting with what was typed first, then the most common
    const rank = (item) => [
      item.text.toLowerCase().startsWith(typed) ? 0 : 1,
      -Number(item.count || 0),
    ];
    return items
      .filter((item) => item.text.toLowerCase().includes(typed))
      .sort((a, b) => {
        const [x, y] = [rank(a), rank(b)];
        return x[0] - y[0] || x[1] - y[1];
      })
      .slice(0, SUGGESTIONS);
  }

  let shownSuggestions = [];
  let active = -1;

  function renderSuggestions() {
    const typed = search.value.trim().toLowerCase();
    shownSuggestions = typed.length < 2 ? [] : suggestionsFor(typed);
    active = -1;
    suggestions.replaceChildren(
      ...shownSuggestions.map((item, i) => {
        const option = document.createElement("li");
        option.id = `eg-suggestion-${i}`;
        option.className = "eg-suggestion";
        option.setAttribute("role", "option");
        for (const [className, text] of [
          ["eg-suggestion-kind", item.kind],
          ["eg-suggestion-text", item.text],
          ["eg-n", item.count ?? ""],
        ]) {
          const span = document.createElement("span");
          span.className = className;
          span.textContent = text;
          option.append(span);
        }
        // mousedown, so the search box keeps focus and doesn't close the list first
        option.addEventListener("mousedown", (event) => {
          event.preventDefault();
          choose(item);
        });
        return option;
      }),
    );
    suggestions.hidden = shownSuggestions.length === 0;
    search.setAttribute("aria-expanded", !suggestions.hidden);
    search.removeAttribute("aria-activedescendant");
  }

  function closeSuggestions() {
    suggestions.hidden = true;
    search.setAttribute("aria-expanded", false);
    search.removeAttribute("aria-activedescendant");
  }

  function choose(item) {
    closeSuggestions();
    // Only navigate: updating the URL in place would cancel the navigation
    if (item.href) return window.location.assign(item.href);
    item.pick();
    update();
  }

  // Links from before the redesign use ?filters=cloud/aws/ec2,library/cuml,workflow/hpo
  function legacyFilter(tag) {
    const [root, ...rest] = tag.split("/");
    const value = aliases[rest.join("/")] || rest.join("/");
    const dataRoots = {
      dataset: "dataset",
      "data-format": "format",
      "data-storage": "storage",
    };
    if (tag === "cloud/azure/ml") return ["platform", "cloud/azure/azureml"];
    if (tag === "platforms/hpc") return ["platform", "hpc"];
    if (root === "cloud" || root === "platforms") return ["platform", tag];
    if (root in dataRoots) return [dataRoots[root], value];
    if (root === "library") return ["library", value];
    if (root === "workflow")
      return box("task", value) ? ["task", value] : ["library", value];
    return null;
  }

  function readUrl() {
    const params = new URLSearchParams(window.location.search);
    const wanted = facets.flatMap((facet) =>
      (params.get(facet) || "").split(",").map((value) => [facet, value]),
    );
    const words = [params.get("search") || ""];
    (params.get("filters") || "")
      .split(",")
      .filter(Boolean)
      .forEach((tag) => {
        const pair = legacyFilter(tag);
        // Old tags with no filter now, like tools/dask-cuda, become a search.
        // Hyphens become spaces, as the search index splits words on them
        if (pair && box(...pair)) wanted.push(pair);
        else words.push(tag.split("/").slice(1).join(" ").replaceAll("-", " "));
      });
    wanted.forEach((pair) => {
      const input = box(...pair);
      if (input) input.checked = true;
    });
    search.value = words.filter(Boolean).join(" ");
  }

  buttons.forEach((button) =>
    button.addEventListener("click", () => {
      const current = selected("platform");
      const value = button.dataset.value;
      // Clicking the only picked platform (or its provider) again clears it
      const pressed = current.length === 1 && groupValue(current[0]) === value;
      selectOnlyPlatform(pressed ? null : value);
    }),
  );
  gallery.querySelector(".eg-more").addEventListener("click", () => {
    menus.forEach((menu) => (menu.open = menu === platformMenu));
    platformMenu.querySelector("summary").focus();
  });
  gallery
    .querySelector(".eg-empty .eg-clear")
    .addEventListener("click", clearAll);
  facets.forEach((facet) =>
    boxes(facet).forEach((input) => input.addEventListener("change", update)),
  );
  search.addEventListener("input", () => {
    update();
    renderSuggestions();
  });
  search.addEventListener("focus", renderSuggestions);
  search.addEventListener("blur", closeSuggestions);
  search.addEventListener("keydown", (event) => {
    if (suggestions.hidden) return;
    const options = [...suggestions.children];
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const step = event.key === "ArrowDown" ? 1 : -1;
      active = (active + step + options.length) % options.length;
      options.forEach((option, i) =>
        option.setAttribute("aria-selected", i === active),
      );
      search.setAttribute("aria-activedescendant", options[active].id);
    } else if (event.key === "Enter") {
      // Pick the highlighted suggestion, or with none highlighted just close the list
      event.preventDefault();
      if (active >= 0) choose(shownSuggestions[active]);
      else closeSuggestions();
    } else if (event.key === "Escape") {
      // Close the list without the browser also clearing the search box
      event.preventDefault();
      closeSuggestions();
    }
  });

  // One dropdown open at a time, closed by clicking elsewhere or pressing Escape
  menus.forEach((menu) =>
    menu
      .querySelector("summary")
      .addEventListener("click", () =>
        menus.forEach((other) => other !== menu && (other.open = false)),
      ),
  );
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".eg-facet, .eg-more"))
      menus.forEach((menu) => (menu.open = false));
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") menus.forEach((menu) => (menu.open = false));
  });

  readUrl();
  update();
  // Search again once searchindex.js has loaded, in case it arrived after this script
  window.addEventListener("load", update);
});
