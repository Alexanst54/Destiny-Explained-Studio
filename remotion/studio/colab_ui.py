"""Dynamic, vertically stacked controls; no unsupported model option is displayed."""
import json,re
from pathlib import Path
from production import options,validate,LANGUAGES,RESOLUTIONS

def form(drive_root):
 import ipywidgets as w
 from IPython.display import display
 models=options();by_id={m['id']:m for m in models};layout=w.Layout(width='100%')
 boss=w.Dropdown(description='Boss',options=[(m['name']+(' [prototype]' if m['status']=='partial' else ''),m['id']) for m in models],layout=layout)
 arena=w.Dropdown(description='Arène',layout=layout);animation=w.Dropdown(description='Animation',layout=layout);camera=w.Dropdown(description='Caméra',layout=layout)
 def update(change=None):
  m=by_id[boss.value];arena.options=[m['implementation']['environmentId']];animation.options=m['implementation']['animations'];camera.options=m['cameras']
  camera.value='cinematic' if 'cinematic' in m['cameras'] else 'environment'
 boss.observe(update,names='value');update()
 quality=w.Dropdown(description='Qualité',options=['draft','balanced','cinematic'],value='balanced',layout=layout)
 duration=w.BoundedFloatText(description='Secondes',min=2,max=600,value=10,layout=layout)
 language=w.Dropdown(description='Language',options=['fr-FR','en-US'],value='fr-FR',layout=layout)
 voice=w.Dropdown(description='Voice',options=LANGUAGES['fr-FR']['voices'],layout=layout)
 def update_language(change):
  voice.options=LANGUAGES[language.value]['voices']
  if text.value in [x['smoke'] for x in LANGUAGES.values()]:text.value=LANGUAGES[language.value]['smoke']
 language.observe(update_language,names='value')
 text=w.Textarea(description='Narration',value='Voici ce boss.',layout=w.Layout(width='100%',height='150px'))
 subtitles=w.Checkbox(description='Sous-titres',value=True)
 resolution=w.Dropdown(description='Résolution',options=list(RESOLUTIONS),value='Preview',layout=layout)
 fps=w.Dropdown(description='FPS',options=[24,30],value=24,layout=layout)
 destination=w.Text(description='Drive',value=str(Path(drive_root)/'Destiny-Studio'),layout=layout)
 project=w.Text(description='Projet',value='destiny-001',layout=layout)
 music=w.Text(description='Musique',placeholder='Facultatif : chemin Drive du fichier fourni',layout=layout)
 credit=w.Text(description='Crédit',placeholder='Provenance / licence de la musique fournie',layout=layout)
 save=w.Button(description='Enregistrer le projet',button_style='primary',layout=layout);out=w.Output()
 state={}
 def commit(_):
  with out:
   out.clear_output();state.clear()
   try:
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',project.value):raise ValueError('Nom de projet : lettres, chiffres, tirets uniquement.')
    dest=Path(destination.value).expanduser().resolve()
    if not dest.is_relative_to(Path(drive_root).resolve()):raise ValueError('Choisissez une destination dans votre Google Drive monté.')
    width,height=RESOLUTIONS[resolution.value]
    c=validate(dict(boss=boss.value,arena=arena.value,animation=animation.value,camera=camera.value,quality=quality.value,duration=duration.value,language=language.value,narration=text.value,voice=voice.value,subtitles=subtitles.value,width=width,height=height,fps=fps.value,music=music.value.strip(),musicCredit=credit.value.strip()))
    folder=dest/project.value;folder.mkdir(parents=True,exist_ok=True);path=folder/'selection.json'
    # Selection file is editable; immutable production manifest rejects incompatible resume.
    path.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');state.update(config=str(path),folder=str(folder));print('Projet enregistré :',folder,'\nExécutez maintenant le smoke-test. Tout changement de paramètres de production exige un nouveau nom de projet.')
   except Exception as e:print('Configuration refusée :',str(e))
 save.on_click(commit)
 display(w.VBox([w.HTML('<b>Destiny Studio — sélection réelle de l’Atlas</b>'),boss,arena,animation,camera,quality,duration,language,text,voice,subtitles,resolution,fps,destination,project,music,credit,save,out],layout=layout))
 return state
