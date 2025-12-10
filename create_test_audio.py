#!/usr/bin/env python3
"""Create a simulated French doctor-patient conversation audio file."""
from gtts import gTTS
import os
from pathlib import Path

# French medical conversation
conversation = """
Bonjour docteur, je suis venu vous voir car j'ai des maux de tête depuis une semaine.

Bonjour, pouvez-vous me décrire ces maux de tête ? Quand ont-ils commencé ?

Ils ont commencé il y a environ une semaine. C'est une douleur constante, surtout le matin. Parfois, j'ai aussi des nausées.

Avez-vous pris des médicaments pour cela ?

Oui, j'ai pris du paracétamol, mais ça n'aide pas beaucoup. Je prends 500 milligrammes deux fois par jour.

Avez-vous d'autres symptômes ? Des problèmes de vision, de la fièvre ?

Non, pas de problèmes de vision. Mais je me sens très fatigué ces derniers temps, et j'ai du mal à dormir.

Je vois. Avez-vous des antécédents médicaux ? Des allergies ?

Non, pas d'allergies connues. J'ai de l'hypertension, mais je prends des médicaments pour ça. Du lisinopril, 10 milligrammes par jour.

D'accord. Je vais vous examiner. Pouvez-vous me dire si la douleur s'aggrave avec la lumière ou le bruit ?

Oui, la lumière me dérange beaucoup. Et le bruit aussi, surtout le matin.

Très bien. Je pense que vous pourriez avoir des migraines. Je vais vous prescrire de l'ibuprofène, 400 milligrammes trois fois par jour après les repas. Et je vous recommande de prendre du repos, d'éviter le stress, et de bien vous hydrater.

D'accord docteur. Combien de temps dois-je prendre ce médicament ?

Prenez-le pendant une semaine. Si les symptômes persistent ou s'aggravent, revenez me voir. Je vais aussi vous donner une ordonnance pour un examen sanguin pour vérifier votre tension artérielle et votre taux de sucre.

Merci docteur. Quand dois-je revenir pour un suivi ?

Revenez dans deux semaines pour un suivi. En attendant, si vous avez des questions ou si les symptômes s'aggravent, n'hésitez pas à m'appeler.

Merci beaucoup docteur, au revoir.

Au revoir, prenez soin de vous.
"""

def create_audio_file():
    """Create French audio file from conversation."""
    output_dir = Path("data/conversations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "test_conversation_fr.mp3"
    
    print("Creating French audio file...")
    tts = gTTS(text=conversation, lang='fr', slow=False)
    tts.save(str(output_file))
    
    print(f"✅ Audio file created: {output_file}")
    print(f"   File size: {output_file.stat().st_size / 1024:.2f} KB")
    
    return output_file

if __name__ == "__main__":
    audio_file = create_audio_file()
    print(f"\nYou can now upload this file: {audio_file}")

