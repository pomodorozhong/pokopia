export function rankItems(pokemon, favoriteItems) {
  if (!pokemon.length) return []

  const groupFavoriteKeys = new Set()
  const pokemonByFavorite = new Map()

  for (const p of pokemon) {
    for (const fav of p.favorites) {
      groupFavoriteKeys.add(fav)
      if (!pokemonByFavorite.has(fav)) pokemonByFavorite.set(fav, [])
      pokemonByFavorite.get(fav).push(p)
    }
  }

  const scored = new Map()

  for (const fav of groupFavoriteKeys) {
    const slugs = favoriteItems[fav] || []
    for (const slug of slugs) {
      let entry = scored.get(slug)
      if (!entry) {
        entry = {
          slug,
          matchedFavorites: new Set(),
          benefiting: new Map(),
          pairHits: 0,
        }
        scored.set(slug, entry)
      }
      entry.matchedFavorites.add(fav)
      for (const p of pokemonByFavorite.get(fav) || []) {
        entry.benefiting.set(p.name_en, p)
        entry.pairHits += 1
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
  }))

  rows.sort((a, b) => {
    if (b.criteriaScore !== a.criteriaScore) return b.criteriaScore - a.criteriaScore
    if (b.pokemonScore !== a.pokemonScore) return b.pokemonScore - a.pokemonScore
    if (b.pairHits !== a.pairHits) return b.pairHits - a.pairHits
    return a.slug < b.slug ? -1 : a.slug > b.slug ? 1 : 0
  })

  return rows
}

/** Rank other Pokémon by shared favorites with the selected group (Mode 2). */
export function rankSimilarPokemon(selectedPokemon, allPokemon) {
  if (!selectedPokemon.length) return []

  const selectedNames = new Set(selectedPokemon.map((p) => p.name_en))
  const groupFavoriteKeys = new Set()
  const pokemonByFavorite = new Map()

  for (const p of selectedPokemon) {
    for (const fav of p.favorites) {
      groupFavoriteKeys.add(fav)
      if (!pokemonByFavorite.has(fav)) pokemonByFavorite.set(fav, [])
      pokemonByFavorite.get(fav).push(p)
    }
  }

  if (!groupFavoriteKeys.size) return []

  const rows = []

  for (const candidate of allPokemon) {
    if (selectedNames.has(candidate.name_en)) continue

    const matchedFavorites = []
    const benefiting = new Map()
    let pairHits = 0

    for (const fav of candidate.favorites) {
      if (!groupFavoriteKeys.has(fav)) continue
      matchedFavorites.push(fav)
      for (const p of pokemonByFavorite.get(fav) || []) {
        benefiting.set(p.name_en, p)
        pairHits += 1
      }
    }

    if (!matchedFavorites.length) continue

    matchedFavorites.sort()
    rows.push({
      pokemon: candidate,
      criteriaScore: matchedFavorites.length,
      pokemonScore: benefiting.size,
      pairHits,
      matchedFavorites,
      benefiting: [...benefiting.values()],
    })
  }

  rows.sort((a, b) => {
    if (b.criteriaScore !== a.criteriaScore) return b.criteriaScore - a.criteriaScore
    if (b.pokemonScore !== a.pokemonScore) return b.pokemonScore - a.pokemonScore
    if (b.pairHits !== a.pairHits) return b.pairHits - a.pairHits
    return a.pokemon.name_en < b.pokemon.name_en
      ? -1
      : a.pokemon.name_en > b.pokemon.name_en
        ? 1
        : 0
  })

  return rows
}

export function pokemonMatchesQuery(p, q, habitatLabelFn, favoriteLabelFn) {
  if (!q) return true
  const hay = [
    p.name_en,
    p.names?.en,
    p.names?.ja,
    p.names?.zh_tw,
    p.ideal_habitat,
    habitatLabelFn(p.ideal_habitat),
    p.primary_location,
    ...p.favorites.map((f) => favoriteLabelFn(f)),
    ...p.favorites,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
  return hay.includes(q)
}
