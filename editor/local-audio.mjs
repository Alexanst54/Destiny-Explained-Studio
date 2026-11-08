// This object stays in memory only. No upload, data URI, or persistence in project JSON.
export function createLocalNarration(file,urlApi=URL){
 if(!file||!(/\.(wav|mp3)$/i.test(file.name)||['audio/wav','audio/x-wav','audio/mpeg'].includes(file.type)))throw new Error('Choisissez un fichier WAV ou MP3 local.');
 if(file.size>50*1024*1024)throw new Error('Narration supérieure à 50 Mio : utilisez un fichier plus léger.');
 const url=urlApi.createObjectURL(file);let released=false;
 return {name:file.name,url,file,dispose(){if(!released){urlApi.revokeObjectURL(url);released=true;}}};
}
export function narrationDuration(url){
 return new Promise((resolve,reject)=>{const audio=new Audio();let timer;
  const cleanup=()=>{clearTimeout(timer);audio.onloadedmetadata=null;audio.onerror=null;audio.removeAttribute('src');audio.load();};
  audio.preload='metadata';audio.onloadedmetadata=()=>{const duration=audio.duration;cleanup();Number.isFinite(duration)?resolve(duration):reject(new Error('Durée audio inconnue.'));};
  audio.onerror=()=>{cleanup();reject(new Error('Ce fichier audio ne peut pas être lu par le navigateur.'));};
  timer=setTimeout(()=>{cleanup();reject(new Error('Chargement audio trop long ; réessayez avec un WAV ou MP3 plus léger.'));},10000);audio.src=url;
 });
}
