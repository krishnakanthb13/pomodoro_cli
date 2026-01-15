import wave
import math
import struct
import os

SAMPLE_RATE = 44100

def generate_calm_sine(frequency, duration_ms, volume=0.3):
    """
    Generate a very pure, soft sine wave.
    No complex harmonics, no harsh attacks.
    """
    if frequency == 0:
        return [0.0] * int(SAMPLE_RATE * duration_ms / 1000)

    num_samples = int(SAMPLE_RATE * duration_ms / 1000)
    samples = []
    
    # Soft envelope to prevent clicking
    # For a flute/breath feel, the attack is soft but distinct
    attack_ms = 150
    decay_ms = 150
    attack_samples = int(SAMPLE_RATE * attack_ms / 1000)
    decay_samples = int(SAMPLE_RATE * decay_ms / 1000)
    
    # Safety clamp for short sounds
    if attack_samples + decay_samples > num_samples:
        attack_samples = num_samples // 2
        decay_samples = num_samples // 2

    for i in range(num_samples):
        t = float(i) / SAMPLE_RATE
        
        # Pure Sine Wave - The most calming sound
        # Added a tiny bit of 2nd harmonic for 'woodwind' character, but very subtle
        val = math.sin(2.0 * math.pi * frequency * t)
        val += 0.2 * math.sin(2.0 * math.pi * (frequency * 2) * t) # Octave, soft
        
        # Normalize roughly (1.0 + 0.2 = 1.2 max)
        val /= 1.2
        
        # Apply Envelope (Fade In / Fade Out)
        envelope = 1.0
        if i < attack_samples:
            # Linear fade in
            envelope = i / float(attack_samples)
        elif i > num_samples - decay_samples:
            # Linear fade out
            remaining = num_samples - i
            envelope = remaining / float(decay_samples)
            
        # Apply master volume
        val *= volume * envelope
        
        samples.append(val)
        
    return samples

def save_wav(filename, sequence):
    all_samples = []
    # 50ms silence start
    all_samples.extend([0.0] * int(SAMPLE_RATE * 0.05))
    
    for freq, dur in sequence:
        all_samples.extend(generate_calm_sine(freq, dur))
        # 20ms silence between notes for articulation
        all_samples.extend([0.0] * int(SAMPLE_RATE * 0.02))

    packed_data = bytearray()
    for s in all_samples:
        s = max(min(s, 1.0), -1.0) # Hard clip safety
        s_int = int(s * 32767)
        packed_data.extend(struct.pack('<h', s_int))
        
    os.makedirs('sounds', exist_ok=True)
    fullpath = os.path.join('sounds', filename)
    
    with wave.open(fullpath, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(packed_data)
    print(f"Generated {fullpath}")

# Musical Notes (Pentatonic / Major scales - universally pleasant)
# Lower Octave (Calm, Deep)
G3 = 196.00; A3 = 220.00; B3 = 246.94
C4 = 261.63; D4 = 293.66; E4 = 329.63; F4 = 349.23; G4 = 392.00; A4 = 440.00
C5 = 523.25; D5 = 587.33; E5 = 659.25

# 1. Deep Flow (90m) - "Slow and Long"
# Very long, breathing notes. Low pitch.
# C4 -> G4 -> C5 (Perfect Fifth / Octave intervals are very stable)
seq1 = [(C4, 1500), (0, 200), (G4, 1500), (0, 200), (C4, 2000)]
save_wav("deep_flow.wav", seq1)

# 2. Deep Work (50m) - Grounded
# Just two slow notes rocking back and forth.
seq2 = [(A3, 1200), (0, 100), (C4, 1200), (0, 100), (A3, 1500)]
save_wav("deep_work.wav", seq2)

# 3. Extended Focus (45m)
seq3 = [(D4, 1000), (0, 50), (A4, 1000), (0, 50), (D4, 1200)]
save_wav("extended_focus.wav", seq3)

# 4. Study Session (30m) - slightly brighter
seq4 = [(E4, 800), (G4, 800), (C5, 1000)]
save_wav("study_session.wav", seq4)

# 5. Classic Pomodoro (25m) - "The Standard"
# Simple ascending triad. 
seq5 = [(C4, 400), (E4, 400), (G4, 400), (C5, 800)]
save_wav("classic_pomodoro.wav", seq5)

# 6. Quick Sprint (15m) - "Quick flute beats"
# Shorter, playful, but NOT harsh.
seq6 = [(G4, 200), (A4, 200), (C5, 200), (E5, 400)]
save_wav("quick_sprint.wav", seq6)

# 7. Ultra Sprint (10m) - Fast
G5 = 783.99 # Defining G5 locally
seq7 = [(C5, 150), (E5, 150), (G5, 150), (C5*2, 300)]
save_wav("ultra_sprint.wav", seq7)

# 8. Custom / Test
seq8 = [(440, 500)]
save_wav("custom_setup.wav", seq8)
save_wav("test_mode.wav", seq8)

print("Regenerated sounds: Pure sine waves, soft envelopes, no harshness.")
