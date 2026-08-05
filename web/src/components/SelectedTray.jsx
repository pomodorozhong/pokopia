import { assetUrl } from '../i18n'
import { localizeName } from '../lib/labels'

export default function SelectedTray({ pokemon, lang, onRemove }) {
  if (!pokemon.length) return null

  return (
    <div className="selected-tray">
      {pokemon.map((p) => (
        <span key={p.name_en} className="selected-chip">
          <img src={assetUrl(`icons/pokemon/${p.icon}.png`)} alt="" loading="lazy" />
          <span>{localizeName(p.names, lang, p.name_en)}</span>
          <button
            type="button"
            aria-label="Remove"
            onClick={() => onRemove(p.name_en)}
          >
            ×
          </button>
        </span>
      ))}
    </div>
  )
}
