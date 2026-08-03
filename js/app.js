const I18N = {
  en: {
    mode1_num: "Mode 1",
    mode1_title: "Pokémon → Items",
    mode2_num: "Mode 2",
    mode2_title: "Coming soon",
    mode1_lede:
      "Pick the Pokémon you want to house together. We’ll rank items that match their favorites, and warn you when Ideal Habitats clash.",
    picker_heading: "Choose Pokémon",
    results_heading: "Suggested items",
    search_placeholder: "Search by name, habitat, or favorite…",
    clear: "Clear",
    min_score: "Min matches",
    results_empty: "Select at least one Pokémon to see ranked items.",
    results_filtered: "No items reach the minimum match count. Try lowering the filter.",
    score_label: "matches",
    liked_by: "Liked by",
    warning_title: "Ideal Habitat conflict",
    warning_intro: "These Pokémon prefer opposite conditions in the same living area:",
    footer_note:
      "Fan tool for Pokémon Pokopia. Unofficial — not affiliated with Nintendo, The Pokémon Company, or Game Freak.",
    vs: "vs",
  },
  ja: {
    mode1_num: "モード1",
    mode1_title: "ポケモン → アイテム",
    mode2_num: "モード2",
    mode2_title: "近日公開",
    mode1_lede:
      "同じ場所に住ませたいポケモンを選ぶと、好みに合うアイテムを優先度つきで表示します。理想の環境がぶつかる場合は警告します。",
    picker_heading: "ポケモンを選ぶ",
    results_heading: "おすすめアイテム",
    search_placeholder: "名前・環境・好みで検索…",
    clear: "クリア",
    min_score: "最低一致数",
    results_empty: "ポケモンを選ぶと、ランキングが表示されます。",
    results_filtered: "最低一致数に達するアイテムがありません。フィルターを下げてみてください。",
    score_label: "一致",
    liked_by: "好きなポケモン",
    warning_title: "理想の環境の衝突",
    warning_intro: "同じ場所で正反対の環境を好むポケモンがいます：",
    footer_note:
      "『Pokémon Pokopia』のファン向けツールです。任天堂・ポケモン・ゲームフリーク公式ではありません。",
    vs: "対",
  },
  zh_tw: {
    mode1_num: "模式 1",
    mode1_title: "寶可夢 → 道具",
    mode2_num: "模式 2",
    mode2_title: "即將推出",
    mode1_lede:
      "選擇想放在同一生活區的寶可夢，依喜好排出適合的道具；若理想環境互相衝突會顯示警告。",
    picker_heading: "選擇寶可夢",
    results_heading: "推薦道具",
    search_placeholder: "依名稱、環境或喜好搜尋…",
    clear: "清除",
    min_score: "最低相符數",
    results_empty: "請先選擇至少一隻寶可夢。",
    results_filtered: "沒有達到最低相符數的道具，請調低篩選條件。",
    score_label: "相符",
    liked_by: "喜歡的寶可夢",
    warning_title: "理想環境衝突",
    warning_intro: "這些寶可夢在同一生活區偏好相反的環境：",
    footer_note:
      "寶可夢 Pokopia 粉絲工具。非官方，與任天堂、寶可夢公司或 Game Freak 無關。",
    vs: "對",
  },
};

const state = {
  data: null,
  lang: localStorage.getItem("pokopia-planner-lang") || "en",
  selected: new Set(),
  query: "",
  minScore: 2,
};

const els = {};

function t(key) {
  return I18N[state.lang]?.[key] ?? I18N.en[key] ?? key;
}

function localizeName(names, fallback = "") {
  if (!names) return fallback;
  return names[state.lang] || names.en || fallback;
}

function favoriteLabel(key) {
  const fav = state.data.favorites[key];
  if (!fav) return key;
  return fav[state.lang] || fav.en || key;
}

function habitatLabel(key) {
  if (!key) return "";
  const h = state.data.ideal_habitats[key];
  if (!h) return key;
  return h[state.lang] || h.en || key;
}

function itemLabel(slug) {
  const item = state.data.items[slug];
  if (!item) return slug;
  return item[state.lang] || item.en || slug;
}

function itemCategory(slug) {
  const item = state.data.items[slug];
  if (!item?.category) return "";
  const raw = item.category;
  // localization item_categories keys are lowercase slugs; CSV/Infipoke use display EN
  const key = Object.keys(state.data.item_categories || {}).find((k) => {
    const cat = state.data.item_categories[k];
    return (
      k === raw.toLowerCase().replace(/\s+/g, "_") ||
      cat.en?.toLowerCase() === raw.toLowerCase()
    );
  });
  if (key) {
    const cat = state.data.item_categories[key];
    return cat[state.lang] || cat.en || raw;
  }
  return raw;
}

function pokemonIcon(p) {
  return `icons/pokemon/${p.icon}.png`;
}

function itemIcon(slug) {
  return `icons/items/${slug}.png`;
}

function applyI18n() {
  document.documentElement.lang =
    state.lang === "zh_tw" ? "zh-Hant" : state.lang === "ja" ? "ja" : "en";

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
}

function selectedPokemon() {
  return state.data.pokemon.filter((p) => state.selected.has(p.name_en));
}

function detectHabitatConflicts(pokemon) {
  const byHabitat = new Map();
  for (const p of pokemon) {
    if (!p.ideal_habitat) continue;
    if (!byHabitat.has(p.ideal_habitat)) byHabitat.set(p.ideal_habitat, []);
    byHabitat.get(p.ideal_habitat).push(p);
  }

  const conflicts = [];
  for (const [a, b] of state.data.habitat_conflicts) {
    if (byHabitat.has(a) && byHabitat.has(b)) {
      conflicts.push({
        pair: [a, b],
        left: byHabitat.get(a),
        right: byHabitat.get(b),
      });
    }
  }
  return conflicts;
}

function renderHabitatWarning() {
  const box = els.habitatWarning;
  const selected = selectedPokemon();
  const conflicts = detectHabitatConflicts(selected);

  if (!conflicts.length) {
    box.hidden = true;
    box.innerHTML = "";
    return;
  }

  const items = conflicts
    .map((c) => {
      const leftNames = c.left.map((p) => localizeName(p.names, p.name_en)).join(", ");
      const rightNames = c.right.map((p) => localizeName(p.names, p.name_en)).join(", ");
      return `<li><strong>${habitatLabel(c.pair[0])}</strong> (${leftNames})
        ${t("vs")}
        <strong>${habitatLabel(c.pair[1])}</strong> (${rightNames})</li>`;
    })
    .join("");

  box.hidden = false;
  box.innerHTML = `
    <strong>${t("warning_title")}</strong>
    <div>${t("warning_intro")}</div>
    <ul>${items}</ul>
  `;
}

function renderSelectedTray() {
  const tray = els.selectedTray;
  const selected = selectedPokemon();
  els.selectedCount.textContent = String(selected.length);

  if (!selected.length) {
    tray.hidden = true;
    tray.innerHTML = "";
    return;
  }

  tray.hidden = false;
  tray.innerHTML = selected
    .map(
      (p) => `
      <span class="selected-chip">
        <img src="${pokemonIcon(p)}" alt="" loading="lazy" />
        <span>${localizeName(p.names, p.name_en)}</span>
        <button type="button" data-remove="${p.name_en}" aria-label="Remove">×</button>
      </span>`
    )
    .join("");
}

function pokemonMatchesQuery(p, q) {
  if (!q) return true;
  const hay = [
    p.name_en,
    p.names?.en,
    p.names?.ja,
    p.names?.zh_tw,
    p.ideal_habitat,
    habitatLabel(p.ideal_habitat),
    p.primary_location,
    ...p.favorites.map((f) => favoriteLabel(f)),
    ...p.favorites,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  return hay.includes(q);
}

function renderPokemonGrid() {
  const q = state.query.trim().toLowerCase();
  const html = [];

  for (const p of state.data.pokemon) {
    const match = pokemonMatchesQuery(p, q);
    const selected = state.selected.has(p.name_en);
    if (!match && !selected) continue;

    html.push(`
      <button
        type="button"
        class="poke-card${selected ? " is-selected" : ""}${!match ? " is-dim" : ""}"
        role="option"
        aria-selected="${selected}"
        data-name="${p.name_en}"
        title="${p.favorites.map((f) => favoriteLabel(f)).join(" · ")}"
      >
        <img src="${pokemonIcon(p)}" alt="" loading="lazy" />
        <span class="name">${localizeName(p.names, p.name_en)}</span>
        <span class="habitat" data-h="${p.ideal_habitat || ""}">${habitatLabel(p.ideal_habitat)}</span>
      </button>
    `);
  }

  els.pokemonGrid.innerHTML = html.join("");
}

function rankItems(pokemon) {
  if (!pokemon.length) return [];

  const groupFavoriteKeys = new Set();
  const pokemonByFavorite = new Map();

  for (const p of pokemon) {
    for (const fav of p.favorites) {
      groupFavoriteKeys.add(fav);
      if (!pokemonByFavorite.has(fav)) pokemonByFavorite.set(fav, []);
      pokemonByFavorite.get(fav).push(p);
    }
  }

  const scored = new Map();

  for (const fav of groupFavoriteKeys) {
    const slugs = state.data.favorite_items[fav] || [];
    for (const slug of slugs) {
      let entry = scored.get(slug);
      if (!entry) {
        entry = {
          slug,
          matchedFavorites: new Set(),
          benefiting: new Map(), // name_en -> pokemon
          pairHits: 0,
        };
        scored.set(slug, entry);
      }
      entry.matchedFavorites.add(fav);
      for (const p of pokemonByFavorite.get(fav) || []) {
        entry.benefiting.set(p.name_en, p);
        entry.pairHits += 1;
      }
    }
  }

  const rows = [...scored.values()].map((entry) => ({
    slug: entry.slug,
    criteriaScore: entry.matchedFavorites.size,
    pokemonScore: entry.benefiting.size,
    pairHits: entry.pairHits,
    matchedFavorites: [...entry.matchedFavorites].sort(),
    benefiting: [...entry.benefiting.values()],
  }));

  // Tie-break by slug only — never pass UI lang keys (e.g. zh_tw) to localeCompare.
  rows.sort((a, b) => {
    if (b.criteriaScore !== a.criteriaScore) return b.criteriaScore - a.criteriaScore;
    if (b.pokemonScore !== a.pokemonScore) return b.pokemonScore - a.pokemonScore;
    if (b.pairHits !== a.pairHits) return b.pairHits - a.pairHits;
    return a.slug < b.slug ? -1 : a.slug > b.slug ? 1 : 0;
  });

  return rows;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderResults() {
  const pokemon = selectedPokemon();
  const ranked = rankItems(pokemon);
  const filtered = ranked.filter((r) => r.criteriaScore >= state.minScore);

  els.resultsCount.textContent = String(filtered.length);

  if (!pokemon.length) {
    els.resultsHint.hidden = false;
    els.resultsHint.textContent = t("results_empty");
    els.resultsList.innerHTML = "";
    return;
  }

  if (!filtered.length) {
    els.resultsHint.hidden = false;
    els.resultsHint.textContent = t("results_filtered");
    els.resultsList.innerHTML = "";
    return;
  }

  els.resultsHint.hidden = true;

  els.resultsList.innerHTML = filtered
    .map((row, index) => {
      const tags = row.matchedFavorites
        .map((f) => `<span class="tag">${escapeHtml(favoriteLabel(f))}</span>`)
        .join("");
      const faces = row.benefiting
        .map((p) => {
          const name = escapeHtml(localizeName(p.names, p.name_en));
          return `<img src="${pokemonIcon(p)}" alt="${name}" title="${name}" loading="lazy" />`;
        })
        .join("");

      return `
        <article class="item-card" style="animation-delay: ${Math.min(index, 12) * 20}ms">
          <img src="${itemIcon(row.slug)}" alt="" loading="lazy" onerror="this.style.opacity=.25" />
          <div>
            <h3 class="item-name">${escapeHtml(itemLabel(row.slug))}</h3>
            <p class="item-cat">${escapeHtml(itemCategory(row.slug))}</p>
            <div class="tag-row">${tags}</div>
            <div class="beneficiaries" aria-label="${escapeHtml(t("liked_by"))}">${faces}</div>
          </div>
          <div class="score-box">
            <span class="score">${row.criteriaScore}</span>
            <span class="score-label">${escapeHtml(t("score_label"))}</span>
          </div>
        </article>
      `;
    })
    .join("");
}

function refresh() {
  try {
    applyI18n();
    renderSelectedTray();
    renderHabitatWarning();
    renderPokemonGrid();
    renderResults();
  } catch (err) {
    console.error(err);
    if (els.resultsHint) {
      els.resultsHint.hidden = false;
      els.resultsHint.textContent = `Error: ${err.message}`;
    }
  }
}

function togglePokemon(name) {
  if (state.selected.has(name)) state.selected.delete(name);
  else state.selected.add(name);
  renderSelectedTray();
  renderHabitatWarning();
  renderPokemonGrid();
  renderResults();
}

function bindEvents() {
  els.langSelect.value = state.lang;
  els.langSelect.addEventListener("change", () => {
    state.lang = els.langSelect.value;
    localStorage.setItem("pokopia-planner-lang", state.lang);
    refresh();
  });

  els.search.addEventListener("input", () => {
    state.query = els.search.value;
    renderPokemonGrid();
  });

  els.clearBtn.addEventListener("click", () => {
    state.selected.clear();
    refresh();
  });

  els.minScore.addEventListener("change", () => {
    state.minScore = Number(els.minScore.value) || 1;
    renderResults();
  });

  els.pokemonGrid.addEventListener("click", (event) => {
    const card = event.target.closest(".poke-card");
    if (!card) return;
    togglePokemon(card.dataset.name);
  });

  els.selectedTray.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-remove]");
    if (!btn) return;
    state.selected.delete(btn.dataset.remove);
    refresh();
  });
}

async function main() {
  els.langSelect = document.getElementById("lang-select");
  els.search = document.getElementById("pokemon-search");
  els.clearBtn = document.getElementById("clear-selection");
  els.selectedTray = document.getElementById("selected-tray");
  els.selectedCount = document.getElementById("selected-count");
  els.habitatWarning = document.getElementById("habitat-warning");
  els.pokemonGrid = document.getElementById("pokemon-grid");
  els.resultsList = document.getElementById("results-list");
  els.resultsHint = document.getElementById("results-hint");
  els.resultsCount = document.getElementById("results-count");
  els.minScore = document.getElementById("min-score");

  state.minScore = Number(els.minScore.value) || 2;

  const res = await fetch("data/planner.json");
  if (!res.ok) throw new Error(`Failed to load planner data (${res.status})`);
  state.data = await res.json();

  // Stable alphabetical order by English name for browsing
  state.data.pokemon.sort((a, b) => a.name_en.localeCompare(b.name_en));

  bindEvents();
  refresh();
}

main().catch((err) => {
  console.error(err);
  document.querySelector(".lede").textContent =
    "Could not load planner data. If you opened the HTML file directly, serve the repo over HTTP (GitHub Pages or a local static server).";
});
