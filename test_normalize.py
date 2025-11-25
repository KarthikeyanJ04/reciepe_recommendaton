import re

def normalize_instructions(instructions):
    """Ensure instructions are a flat list of single steps."""
    if isinstance(instructions, str):
        instructions = [instructions]
    
    normalized = []
    for item in instructions:
        # Split by newlines first
        lines = item.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for numbered list pattern within the line (e.g. "1. Step one. 2. Step two.")
            parts = re.split(r'\s+(?=\d+[\.\)])\s*', line)
            
            for part in parts:
                part = part.strip()
                # Remove leading numbers/bullets
                part = re.sub(r'^\d+[\.\)\-]\s*', '', part)
                if part:
                    normalized.append(part)
    return normalized

def test():
    print("Testing normalize_instructions...")
    
    # Case 1: Already clean
    inp1 = ["Chop onions.", "Fry onions."]
    out1 = normalize_instructions(inp1)
    print(f"Case 1: {out1}")
    assert len(out1) == 2
    
    # Case 2: Combined string
    inp2 = ["1. Chop onions. 2. Fry onions."]
    out2 = normalize_instructions(inp2)
    print(f"Case 2: {out2}")
    assert len(out2) == 2
    assert out2[0] == "Chop onions."
    assert out2[1] == "Fry onions."
    
    # Case 3: Newlines
    inp3 = "Step 1\nStep 2"
    out3 = normalize_instructions(inp3)
    print(f"Case 3: {out3}")
    assert len(out3) == 2
    
    # Case 4: Mixed
    inp4 = ["1. Start.", "2. Middle. 3. End."]
    out4 = normalize_instructions(inp4)
    print(f"Case 4: {out4}")
    assert len(out4) == 3

    print("✅ All tests passed!")

if __name__ == "__main__":
    test()
