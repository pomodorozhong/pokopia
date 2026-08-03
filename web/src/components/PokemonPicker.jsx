import { t } from '../i18n'
import { detectHabitatConflicts } from '../lib/habitat'
import HabitatWarning from './HabitatWarning'
import PokemonGrid from './PokemonGrid'
import SelectedTray from './SelectedTray'

export default function PokemonPicker({
  data,
  lang,
  selected,
  query,
  onQueryChange,
  onToggle,
  onRemove,
  onClear,
}) {
  const selectedPokemon = data.pokemon.filter((p) => selected.has(p.name_en))
  const conflicts = detectHabitatConflicts(
    selectedPokemon,
    data.habitat_conflicts,
  )

  return (
    <section className="panel picker-panel" aria-labelledby="picker-heading">
      <div className="panel-head">
        <h2 id="picker-heading">{t(lang, 'picker_heading')}</h2>
        <span className="count-pill">{selectedPokemon.length}</span>
      </div>

      <div className="search-row">
        <input
          className="pokemon-search"
          type="search"
          autoComplete="off"
          spellCheck="false"
          placeholder={t(lang, 'search_placeholder')}
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
        />
        <button type="button" className="ghost-btn" onClick={onClear}>
          {t(lang, 'clear')}
        </button>
      </div>

      <SelectedTray pokemon={selectedPokemon} lang={lang} onRemove={onRemove} />

      <HabitatWarning conflicts={conflicts} data={data} lang={lang} />

      <PokemonGrid
        pokemon={data.pokemon}
        selected={selected}
        query={query}
        data={data}
        lang={lang}
        onToggle={onToggle}
      />
    </section>
  )
}
