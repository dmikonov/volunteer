import re, importlib.resources as ir
import spaces, gradio as gr, torch, soundfile as sf, tempfile
from huggingface_hub import hf_hub_download as d
from omegaconf import OmegaConf
from f5_tts.model import DiT
from f5_tts.infer.utils_infer import load_model, load_vocoder, infer_process, preprocess_ref_audio_text
from phonikud_onnx import Phonikud
PK = Phonikud(d('thewh1teagle/phonikud-onnx', 'phonikud-1.0.int8.onnx'))
NIKUD = re.compile('[ְ-ׇּׁׂ֫]')
# text that already carries nikud (hand-checked stress) is used as is
voc = lambda t: t if NIKUD.search(t) else PK.add_diacritics(t).replace('|', '')
cfg = OmegaConf.load(str(ir.files('f5_tts').joinpath('configs/F5TTS_v1_Base.yaml'))).model.arch
M = load_model(DiT, dict(cfg), d('Yzamari/f5tts-hebrew-v2', 'model.safetensors'), mel_spec_type='vocos', vocab_file=d('Yzamari/f5tts-hebrew-v2', 'vocab.txt'), device='cpu', use_ema=True).to('cuda')
V = load_vocoder('vocos', device='cpu').to('cuda')

@spaces.GPU(duration=90)
def gen(ref_audio, ref_text, gen_text, speed, nfe, cfg_strength, seed):
    torch.manual_seed(int(seed))
    ra, rt = preprocess_ref_audio_text(ref_audio, voc(ref_text))
    w, sr, _ = infer_process(ra, rt, voc(gen_text), M, V, mel_spec_type='vocos', nfe_step=int(nfe), speed=float(speed), cfg_strength=float(cfg_strength), device='cuda', cross_fade_duration=0.15)
    f = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
    sf.write(f, w, sr)
    return f

def vocalize(text):
    return voc(text)

i1 = gr.Interface(gen, [gr.Audio(type='filepath'), gr.Textbox(), gr.Textbox(), gr.Number(1.0), gr.Number(32), gr.Number(2.0), gr.Number(0)], gr.Audio(type='filepath'), api_name='gen')
i2 = gr.Interface(vocalize, gr.Textbox(), gr.Textbox(), api_name='voc')
gr.TabbedInterface([i1, i2], ['gen', 'voc']).launch()
