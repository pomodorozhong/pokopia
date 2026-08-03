export function localizeName(names, lang, fallback = '') {
  if (!names) return fallback
  return names[lang] || names.en || fallback
}

export function favoriteLabel(data, key, lang) {
  const fav = data.favorites[key]
  if (!fav) return key
  return fav[lang] || fav.en || key
}

export function habitatLabel(data, key, lang) {
  if (!key) return ''
  const h = data.ideal_habitats[key]
  if (!h) return key
  return h[lang] || h.en || key
}

export function itemLabel(data, slug, lang) {
  const item = data.items[slug]
  if (!item) return slug
  return item[lang] || item.en || slug
}

export function itemCategory(data, slug, lang) {
  const item = data.items[slug]
  if (!item?.category) return ''
  const raw = item.category
  const key = Object.keys(data.item_categories || {}).find((k) => {
    const cat = data.item_categories[k]
    return (
      k === raw.toLowerCase().replace(/\s+/g, '_') ||
      cat.en?.toLowerCase() === raw.toLowerCase()
    )
  })
  if (key) {
    const cat = data.item_categories[key]
    return cat[lang] || cat.en || raw
  }
  return raw
}

export function pokemonIcon(p) {
  return `icons/pokemon/${p.icon}.png`
}

export function itemIcon(slug) {
  return `icons/items/${slug}.png`
}
