import { assetUrl } from '../i18n'
import { favoriteLabel, habitatLabel, localizeName } from '../lib/labels'
import { pokemonMatchesQuery } from '../lib/ranking'

export default function PokemonGrid({
  pokemon,
  selected,
  query,
  data,
  lang,
  onToggle,
}) {
  const q = query.trim().toLowerCase()
  const habitatFn = (key) => habitatLabel(data, key, lang)
  const favoriteFn = (key) => favoriteLabel(data, key, lang)

  const cards = []
  for (const p of pokemon) {
    const match = pokemonMatchesQuery(p, q, habitatFn, favoriteFn)
    const isSelected = selected.has(p.name_en)
    if (!match && !isSelected) continue

    const title = p.favorites.map((f) => favoriteFn(f)).join(' · ')
    cards.push(
      <button
        key={p.name_en}
        type="button"
        className={`poke-card${isSelected ? ' is-selected' : ''}${!match ? ' is-dim' : ''}`}
        role="option"
        aria-selected={isSelected}
        title={title}
        onClick={() => onToggle(p.name_en)}
      >
        <img
          src={assetUrl(`icons/pokemon/${p.icon}.png`)}
          alt=""
          loading="lazy"
        />
        <span className="name">{localizeName(p.names, lang, p.name_en)}</span>
        <span className="habitat" data-h={p.ideal_habitat || ''}>
          {habitatFn(p.ideal_habitat)}
        </span>
      </button>,
    )
  }

  return (
    <div className="pokemon-grid" role="listbox" aria-multiselectable="true">
      {cards}
    </div>
  )
}
