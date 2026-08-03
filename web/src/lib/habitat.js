export function detectHabitatConflicts(pokemon, habitatConflicts) {
  const byHabitat = new Map()
  for (const p of pokemon) {
    if (!p.ideal_habitat) continue
    if (!byHabitat.has(p.ideal_habitat)) byHabitat.set(p.ideal_habitat, [])
    byHabitat.get(p.ideal_habitat).push(p)
  }

  const conflicts = []
  for (const [a, b] of habitatConflicts) {
    if (byHabitat.has(a) && byHabitat.has(b)) {
      conflicts.push({
        pair: [a, b],
        left: byHabitat.get(a),
        right: byHabitat.get(b),
      })
    }
  }
  return conflicts
}
