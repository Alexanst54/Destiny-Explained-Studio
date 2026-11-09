# Couverture de l’Atlas universel D1/D2 — première tranche

Revue : 2026-11-09. Issue [#18](https://github.com/Alexanst54/Destiny-Explained-Studio/issues/18). **Couverture partielle** : le mot « universel » désigne le schéma cible, pas l’exhaustivité du contenu ou des assets.

## Chiffres vérifiables

Le catalogue historique conserve **468 lieux et 17 variantes**. La nouvelle couche relie **71 IDs existants**, ajoute **7 lieux nommés sourcés** et relie **14 variantes historiques** sans renommer leurs IDs locaux. Aucun JSON 0.3–0.8 n’est migré automatiquement.

Tranche : **32 activités**, **27 rencontres**, **9 identités de boss**, **2 variantes de boss**. **6 activités** ont des rencontres pilotes ; les **26 autres** restent explicitement not-started. Les activités pilotes restent partial, pas « exhaustives ».

| Inventaire de noms observé | Activités par jeu/version | État attesté au | Source |
| --- | ---: | --- | --- |
| D2 — dungeon — current | 11 | 2026-11-09 | [bungie-activities](https://help.bungie.net/hc/en-us/articles/46668136913172--10-Activities) · List of currently available dungeons |
| D2 — raid — current | 10 | 2026-11-09 | [bungie-activities](https://help.bungie.net/hc/en-us/articles/46668136913172--10-Activities) · List of currently available raids |
| D2 — raid — vaulted | 5 | 2020-11-10 | [bungie-vault](https://help.bungie.net/hc/fr/articles/360049202971-Coffre-de-contenu-de-Destiny) · Années passées → An 4 → Raids |
| D1 — raid — historical | 4 | 2026-11-09 | [bungie-years](https://help.bungie.net/hc/en-us/articles/4408041224852-Years-of-Destiny) · Destiny → Years 1, 2, 3 → Raids |

Les raids repris en D2 sont des activités distinctes de leurs versions D1 ; les 19 lignes de raid ne signifient pas 19 raids narrativement uniques. Eater of Worlds et Spire of Stars sont inclus dans l’inventaire des raids, comme dans la liste historique Bungie. Les 11 donjons correspondent à la liste Bungie consultée à cette date, pas à une constante imposée à toutes les versions futures du schéma.

## Destinations, dimensions, sous-zones et lieux historiques

| ID conservé ou ajouté | Nom | Jeu | Type | Parent | Apparence | Asset Remotion réutilisé |
| --- | --- | --- | --- | --- | --- | --- |
| destiny-universe | Destiny universe | both | universe-realm | — | editorial | atlas-family-cosmic |
| solar-system | Sol System | D2 | stellar-body | destiny-universe | lore | atlas-family-cosmic |
| reef | The Reef | D1 | destination-region | solar-system | gameplay | atlas-family-awoken |
| ascendant-plane | Ascendant Plane | both | universe-realm | destiny-universe | gameplay | atlas-family-hive |
| vex-network | Vex Network | D2 | universe-realm | destiny-universe | gameplay | atlas-family-vex |
| nine-realms | Realms of the Nine | D2 | universe-realm | destiny-universe | gameplay | atlas-family-cosmic |
| jupiter | Jupiter | D2 | stellar-body | solar-system | gameplay | atlas-family-cosmic |
| saturn | Saturn | D2 | stellar-body | solar-system | gameplay | atlas-family-cosmic |
| oort-cloud | Oort Cloud | D2 | stellar-body | solar-system | manifest-only | atlas-family-cosmic |
| earth | Earth | both | stellar-body | solar-system | gameplay | atlas-family-human |
| moon | The Moon | both | stellar-body | earth | gameplay | atlas-family-hive |
| mercury | Mercury | both | stellar-body | solar-system | gameplay | atlas-family-vex |
| venus | Venus | both | stellar-body | solar-system | gameplay | atlas-family-vex |
| mars | Mars | both | stellar-body | solar-system | gameplay | atlas-family-human |
| io | Io | D2 | stellar-body | jupiter | gameplay | atlas-family-vex |
| titan | Titan, Moon of Saturn | D2 | stellar-body | saturn | gameplay | atlas-family-ocean |
| nessus | Nessus | D2 | stellar-body | solar-system | gameplay | atlas-family-vex |
| europa | Europa | D2 | stellar-body | jupiter | gameplay | voxel-europa-v1 |
| neptune | Neptune | D2 | stellar-body | solar-system | gameplay | atlas-family-future-city |
| cosmodrome | Cosmodrome | both | destination-region | earth | gameplay | atlas-family-human |
| edz | European Dead Zone | D2 | destination-region | earth | gameplay | atlas-family-human |
| last-city | The Last City | both | destination-region | earth | gameplay | atlas-family-human |
| europa-regions | Europa | D2 | destination-region | europa | gameplay | atlas-family-ice |
| zone-europa-regions-1142232514 | Clarity Control | D2 | zone | europa-regions | manifest-only | atlas-family-ice |
| dreaming-city | The Dreaming City | D2 | destination-region | reef | gameplay | atlas-family-awoken |
| savathun-throne-world | Savathûn's Throne World | D2 | destination-region | ascendant-plane | gameplay | atlas-family-hive |
| europan-pyramid | The Europan Pyramid | D2 | ship-station | europa | gameplay | voxel-pyramid-v1 |
| derelict-leviathan | Derelict Leviathan | D2 | ship-station | leviathan | gameplay | atlas-family-cabal |
| dreadnaught | Dreadnaught, Rings of Saturn | both | ship-station | saturn | gameplay | atlas-family-hive |
| black-garden | The Black Garden | both | destination-region | destiny-universe | gameplay | voxel-black-garden-v1 |
| pale-heart | The Pale Heart | D2 | destination-region | traveler | gameplay | atlas-family-cosmic |
| kepler | Kepler | D2 | destination-region | oort-cloud | gameplay | atlas-family-cosmic |
| tower | The Tower | D1 | destination-region | last-city | gameplay | voxel-tower-v1 |
| traveler | The Traveler | D1 | ship-station | destiny-universe | gameplay | atlas-family-cosmic |
| leviathan | Leviathan | D2 | ship-station | solar-system | gameplay | atlas-family-cabal |
| vesper-station | Vesper Station | D2 | ship-station | europa | gameplay | atlas-family-bray |
| essence | Essence | D2 | ship-station | destiny-universe | gameplay | atlas-family-pyramid |
| lure | The Lure | D2 | ship-station | savathun-throne-world | gameplay | atlas-family-pyramid |
| fundament | Fundament | D1 | lore-world | destiny-universe | lore | atlas-family-ocean |
| riis | Riis | D2 | lore-world | destiny-universe | cinematic, lore | atlas-family-eliksni |
| deep-stone-site | Deep Stone Crypt | D2 | historical-site | europa | gameplay | atlas-family-bray |
| plaguelands | Plaguelands | D1 | destination-region | cosmodrome | gameplay | atlas-family-human |
| arena-templars-well | Templar's Well | both | arena | vault-of-glass | gameplay | atlas-family-vex |
| arena-glass-throne | Glass Throne | both | arena | vault-of-glass | gameplay | atlas-family-vex |
| oversoul-throne | Oversoul Throne | both | historical-site | ascendant-plane | gameplay | atlas-family-hive |
| dsc-morning-star | Morning Star | D2 | ship-station | europa | gameplay | atlas-family-bray |
| dsc-restricted | Restricted | D2 | arena | europa | gameplay | atlas-family-bray |
| eleusinia | Eleusinia | D2 | historical-site | ascendant-plane | gameplay | atlas-family-awoken |
| arena-erebus | Erebus | D2 | arena | eleusinia | gameplay | atlas-family-awoken |

Les lieux classés lore-world, notamment Riis et Fundament, ne deviennent pas des destinations jouables. L’association d’une activité à un lieu ne transforme pas son parent entier en patrouille disponible. Les sources de provenance héritée restent marquées inherited-not-rechecked. La parenté d’une dimension exprime une organisation documentaire, pas des coordonnées astronomiques.

## Raids, donjons et première tranche d’autres activités

| ID stable | Jeu | Activité | Type | Disponibilité sourcée | Rencontres | Boss / formes reliés |
| --- | --- | --- | --- | --- | ---: | --- |
| activity-vault-of-glass-d1 | D1 | Vault of Glass | raid | historical | 6 (partial) | The Templar; Atheon, Time's Conflux |
| activity-crotas-end-d1 | D1 | Crota's End | raid | historical | 4 (partial) | Ir Yût, the Deathsinger; Crota, Son of Oryx |
| activity-kings-fall-d1 | D1 | King's Fall | raid | historical | 0 (not-started) | à recenser |
| activity-wrath-of-machine-d1 | D1 | Wrath of the Machine | raid | historical | 0 (not-started) | à recenser |
| activity-last-wish-d2 | D2 | Last Wish | raid | current | 0 (not-started) | à recenser |
| activity-garden-of-salvation-d2 | D2 | Garden of Salvation | raid | current | 0 (not-started) | à recenser |
| activity-deep-stone-crypt-d2 | D2 | Deep Stone Crypt | raid | current | 4 (partial) | Crypt Security; Atraks-1, Fallen Exo; Taniks, Reborn; Taniks, the Abomination |
| activity-vault-of-glass-d2 | D2 | Vault of Glass | raid | current | 6 (partial) | The Templar; Atheon, Time's Conflux |
| activity-vow-of-disciple-d2 | D2 | Vow of the Disciple | raid | current | 0 (not-started) | à recenser |
| activity-kings-fall-d2 | D2 | King's Fall | raid | current | 0 (not-started) | à recenser |
| activity-root-of-nightmares-d2 | D2 | Root of Nightmares | raid | current | 0 (not-started) | à recenser |
| activity-crotas-end-d2 | D2 | Crota's End | raid | current | 4 (partial) | Ir Yût, the Deathsinger; Crota, Son of Oryx |
| activity-salvations-edge-d2 | D2 | Salvation's Edge | raid | current | 0 (not-started) | à recenser |
| activity-desert-perpetual-d2 | D2 | The Desert Perpetual | raid | current | 0 (not-started) | à recenser |
| activity-leviathan-raid-d2 | D2 | Leviathan | raid | vaulted | 0 (not-started) | à recenser |
| activity-eater-of-worlds-d2 | D2 | Eater of Worlds | raid | vaulted | 0 (not-started) | à recenser |
| activity-spire-of-stars-d2 | D2 | Spire of Stars | raid | vaulted | 0 (not-started) | à recenser |
| activity-scourge-of-past-d2 | D2 | Scourge of the Past | raid | vaulted | 0 (not-started) | à recenser |
| activity-crown-of-sorrow-d2 | D2 | Crown of Sorrow | raid | vaulted | 0 (not-started) | à recenser |
| activity-shattered-throne-d2 | D2 | The Shattered Throne | dungeon | current | 3 (partial) | Vorgeth, the Boundless Hunger; Dûl Incaru, the Eternal Return |
| activity-pit-of-heresy-d2 | D2 | Pit of Heresy | dungeon | current | 0 (not-started) | à recenser |
| activity-prophecy-d2 | D2 | Prophecy | dungeon | current | 0 (not-started) | à recenser |
| activity-grasp-of-avarice-d2 | D2 | Grasp of Avarice | dungeon | current | 0 (not-started) | à recenser |
| activity-duality-d2 | D2 | Duality | dungeon | current | 0 (not-started) | à recenser |
| activity-spire-of-watcher-d2 | D2 | Spire of the Watcher | dungeon | current | 0 (not-started) | à recenser |
| activity-ghosts-of-deep-d2 | D2 | Ghosts of the Deep | dungeon | current | 0 (not-started) | à recenser |
| activity-warlords-ruin-d2 | D2 | Warlord's Ruin | dungeon | current | 0 (not-started) | à recenser |
| activity-vespers-host-d2 | D2 | Vesper's Host | dungeon | current | 0 (not-started) | à recenser |
| activity-sundered-doctrine-d2 | D2 | Sundered Doctrine | dungeon | current | 0 (not-started) | à recenser |
| activity-equilibrium-d2 | D2 | Equilibrium | dungeon | current | 0 (not-started) | à recenser |
| activity-whisper-d2 | D2 | The Whisper | exotic-mission | current | 0 (not-started) | à recenser |
| activity-menagerie-d2 | D2 | The Menagerie | seasonal-activity | vaulted | 0 (not-started) | à recenser |

current signifie présence dans la liste Bungie observée, sans promesse de droits d’accès, matchmaking ou rotation. vaulted est daté du retrait attesté (2020-11-10 ici), distinct de la date de consultation 2026-11-09 ; il ne garantit pas un retrait permanent. historical pour D1 signifie sortie attestée, pas fermeture de ses serveurs. unknown conserve l’incertitude. `expansion` identifie une ère de sortie ; pour une reprise gratuite, ce champ n’est pas un prérequis de possession.

## Rencontres et arènes pilotes

| Rencontre | Activité | Lieux / arènes attestés | Boss / forme |
| --- | --- | --- | --- |
| encounter-vault-of-glass-d1-open-gate — Open the Vault | activity-vault-of-glass-d1 | vault-of-glass | pas de boss attribué |
| encounter-vault-of-glass-d1-confluxes — Confluxes | activity-vault-of-glass-d1 | arena-templars-well | pas de boss attribué |
| encounter-vault-of-glass-d1-oracles — Oracles | activity-vault-of-glass-d1 | arena-templars-well | pas de boss attribué |
| encounter-vault-of-glass-d1-templar — The Templar | activity-vault-of-glass-d1 | arena-templars-well | boss-templar (primary) |
| encounter-vault-of-glass-d1-gatekeepers — Awaken the Glass Throne | activity-vault-of-glass-d1 | arena-glass-throne | pas de boss attribué |
| encounter-vault-of-glass-d1-atheon — Atheon, Time's Conflux | activity-vault-of-glass-d1 | arena-glass-throne | boss-atheon (primary) |
| encounter-crotas-end-d1-abyss — Enter the Abyss | activity-crotas-end-d1 | oversoul-throne | pas de boss attribué |
| encounter-crotas-end-d1-bridge — Cross the Bridge | activity-crotas-end-d1 | oversoul-throne | pas de boss attribué |
| encounter-crotas-end-d1-ir-yut — Ir Yût, the Deathsinger | activity-crotas-end-d1 | oversoul-throne | boss-ir-yut (primary) |
| encounter-crotas-end-d1-crota — Crota, Son of Oryx | activity-crotas-end-d1 | oversoul-throne | boss-crota (primary) |
| encounter-vault-of-glass-d2-open-gate — Open the Vault | activity-vault-of-glass-d2 | vault-of-glass | pas de boss attribué |
| encounter-vault-of-glass-d2-confluxes — Confluxes | activity-vault-of-glass-d2 | arena-templars-well | pas de boss attribué |
| encounter-vault-of-glass-d2-oracles — Oracles | activity-vault-of-glass-d2 | arena-templars-well | pas de boss attribué |
| encounter-vault-of-glass-d2-templar — The Templar | activity-vault-of-glass-d2 | arena-templars-well | boss-templar (primary) |
| encounter-vault-of-glass-d2-gatekeepers — Awaken the Glass Throne | activity-vault-of-glass-d2 | arena-glass-throne | pas de boss attribué |
| encounter-vault-of-glass-d2-atheon — Atheon, Time's Conflux | activity-vault-of-glass-d2 | arena-glass-throne | boss-atheon (primary) |
| encounter-crotas-end-d2-abyss — Enter the Abyss | activity-crotas-end-d2 | oversoul-throne | pas de boss attribué |
| encounter-crotas-end-d2-bridge — Cross the Bridge | activity-crotas-end-d2 | oversoul-throne | pas de boss attribué |
| encounter-crotas-end-d2-ir-yut — Ir Yût, the Deathsinger | activity-crotas-end-d2 | oversoul-throne | boss-ir-yut (primary) |
| encounter-crotas-end-d2-crota — Crota, Son of Oryx | activity-crotas-end-d2 | oversoul-throne | boss-crota (primary) |
| encounter-deep-stone-crypt-d2-security — Breaching Crypt Security | activity-deep-stone-crypt-d2 | deep-stone-crypt | boss-crypt-security (primary) |
| encounter-deep-stone-crypt-d2-atraks — Dueling the Fallen Exo | activity-deep-stone-crypt-d2 | zone-europa-regions-1142232514, dsc-morning-star | boss-atraks (primary) |
| encounter-deep-stone-crypt-d2-descent — Prevent Europa’s Destruction | activity-deep-stone-crypt-d2 | dsc-morning-star | boss-taniks-variant-reborn (pursuer) |
| encounter-deep-stone-crypt-d2-taniks — The Abomination | activity-deep-stone-crypt-d2 | dsc-restricted | boss-taniks-variant-abomination (primary) |
| encounter-shattered-throne-d2-erebus — Erebus | activity-shattered-throne-d2 | arena-erebus | pas de boss attribué |
| encounter-shattered-throne-d2-vorgeth — Vorgeth, the Boundless Hunger | activity-shattered-throne-d2 | eleusinia | boss-vorgeth (primary) |
| encounter-shattered-throne-d2-dul-incaru — Dûl Incaru, the Eternal Return | activity-shattered-throne-d2 | eleusinia | boss-dul-incaru (primary) |

Les objectifs éditoriaux sont signalés par labelStatus=editorial-objective ; ils ne prétendent pas être des noms officiels d’arène. Crypt Security est classé comme entité de boss mécanique par la source ; cela ne lui invente pas une identité de personnage. Taniks est une identité unique : Reborn et Abomination sont deux variantes D2, avec relations séparées aux rencontres. Reborn est noté pursuer lors de la descente ; il n’est pas présenté comme un boss à tuer à cette étape. Atraks relie plusieurs emplacements (Clarity Control et Morning Star).

## Sources et limites de vérification

**8 sources consultées dans cette tranche**, **84 références héritées non re-téléchargées**. Chaque référence comporte URL, section, date, capacité documentaire et statut de vérification. Les listes de contrôle sont dans [source-evidence.json](../remotion/atlas/universal/source-evidence.json). Les références de manifest et leur preuve 0.3 existante ne sont pas remplacées.

| Source consultée | Sections utilisées | Nature |
| --- | --- | --- |
| [Years of Destiny](https://help.bungie.net/hc/en-us/articles/4408041224852-Years-of-Destiny) | Destiny Years 1–3; Destiny 2 Years 1–8 | primary |
| [Activities — Bungie New Player Guide](https://help.bungie.net/hc/en-us/articles/46668136913172--10-Activities) | Advanced Activities: Dungeons, Raids, Exotic Missions | primary |
| [Coffre de contenu de Destiny](https://help.bungie.net/hc/fr/articles/360049202971-Coffre-de-contenu-de-Destiny) | Années passées → An 4 → Raids / Activités | primary |
| [Vault of Glass — raid](https://www.destinypedia.com/Vault_of_Glass_(raid)) | Infobox; Walkthrough stages 1–7; Bosses | secondary |
| [Crota's End](https://www.destinypedia.com/Crota%27s_End) | Infobox; Walkthrough: Abyss, Bridge, Ir Yût, Crota; Bosses | secondary |
| [Deep Stone Crypt — raid](https://www.destinypedia.com/Deep_Stone_Crypt_(raid)) | Objectives; Bosses; Walkthrough: Crypt Security, Fallen Exo, Descent, Abomination | secondary |
| [The Shattered Throne](https://www.destinypedia.com/The_Shattered_Throne) | Infobox; Walkthrough: Erebus, Vorgeth, Dûl Incaru | secondary |
| [Taniks, the Scarred](https://www.destinypedia.com/Taniks,_the_Scarred) | Identity; appearances; Beyond Light / Deep Stone Crypt forms | secondary |

Les listes Bungie sont prioritaires pour les inventaires et disponibilités. Les articles Destinypedia ont servi aux relations de rencontres, arènes et boss ; ce sont des sources secondaires, pas des modèles géométriques officiels. Leurs références internes peuvent être incomplètes : la revue reste explicite et partielle. Les noms FR non vérifiés conservent l’anglais et le statut untranslated ; aucune traduction n’est présentée comme officielle par défaut.

La traduction FR du Coffre comporte une date d’An 8 différente du calendrier anglais de Years of Destiny. La tranche utilise la section historique An 4 pour les cinq raids retirés et ne reprend pas cette date contradictoire. Une ancienne liste de retraits ne prime pas sur une liste actuelle : The Whisper est actuel dans la page Activities, tandis que The Menagerie reste un exemple historique retiré.

## Lacunes à traiter explicitement

- Les 468 lieux 0.3 restent intacts ; seule une tranche avec fermeture des parents est reliée à ce catalogue. Le reste ne disparaît pas de l’éditeur historique.
- Les 11 donjons de la liste Bungie sont recensés, mais seul le Trône brisé a des rencontres pilotes. La liste n’est pas figée pour les versions futures.
- 19 raids par jeu/version (4 D1 et 15 D2 dont 5 retirés) ; les reprises sont des activités distinctes. Les 6 activités pilotes restent marquées partial.
- Boss et arènes des autres raids/donjons, boss secondaires de quête, labyrinthes et transitions restent à sourcer ; l’absence de relation ne signifie pas absence de boss.
- Assauts, campagnes et activités saisonnières ne sont pas exhaustifs : seuls The Whisper et The Menagerie illustrent ces types dans cette tranche ; aucun assaut n’est encore importé.
- L’extension des reprises désigne leur ère de sortie, pas un prérequis de possession. Première apparition et dates restent null quand non vérifiées.
- Statut actuel d’un lieu laissé unknown : une liste d’activités ne prouve ni patrouille complète ni accès à tout son parent. La page DCV historique ne prouve pas un retrait permanent.
- Noms français de boss et d’arènes non vérifiés : anglais conservé avec statut untranslated, sans invention de nom officiel.
- Les assets de boss manquent ; les familles visuelles sont des reconstructions partagées. Seul le générateur Blender Riis avant le Tourbillon est relié, aucun fichier .blend réutilisable disponible.
- La reprise D2 de King’s Fall est inventoriée, mais son lien reprisal-of attend une source relationnelle dédiée ; ne pas déduire de la seule similitude du nom.
- Tharis Junction est mentionné par Bungie Years of Destiny mais absent du catalogue historique : revue de lieu et de famille reportée, pas de décor inventé.

## Contrôles et périmètre de livraison

Le schéma strict vérifie les IDs indépendants de la langue, sources, dates, jeux, parents/cycles, variantes, assets existants, cardinalités et relations plusieurs-à-plusieurs. Les listes de sources sont comparées aux ensembles d’activités, et non seulement à leur nombre. Les scènes de lore ne peuvent pas servir silencieusement de lieu jouable. Les assets sont vérifiés sur disque et leurs sélecteurs correspondent aux entrées procédurales existantes.

Depuis `remotion/` : `npm run test:atlas:universal`, `npm run typecheck:atlas:universal`, `npm run audit:assets -- --check`, `npm run report:atlas:coverage -- --check`. Les tests historiques restent à exécuter ; le rapport de validation liste ce qui a réellement été lancé.

Cette livraison n’ajoute ni filtres éditeur, ni import incrémental automatisé, ni boss/arènes modélisés, ni migration Blender générale. Ces étapes suivent l’audit et la revue documentaire. La PR #17 reste indépendante et non fusionnée. Aucun rendu de 35 secondes.
