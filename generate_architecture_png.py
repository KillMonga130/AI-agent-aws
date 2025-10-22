"""
Generate Architecture Diagram PNG from Mermaid
Converts the Mermaid diagram to a high-quality PNG for hackathon submission
"""

import subprocess
import sys
import os

def check_mmdc_installed():
    """Check if mermaid-cli (mmdc) is installed"""
    try:
        result = subprocess.run(['mmdc', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def install_mmdc():
    """Instructions to install mermaid-cli"""
    print("=" * 70)
    print("📦 Mermaid CLI (mmdc) is not installed.")
    print("=" * 70)
    print("\n🔧 INSTALLATION OPTIONS:\n")
    print("Option 1 - NPM (Recommended):")
    print("  npm install -g @mermaid-js/mermaid-cli")
    print("\nOption 2 - Chocolatey (Windows):")
    print("  choco install mermaid-cli")
    print("\nOption 3 - Use Online Tool:")
    print("  1. Visit: https://mermaid.live/")
    print("  2. Copy the Mermaid code from architecture-diagram.md")
    print("  3. Paste and click 'Export as PNG'")
    print("  4. Save as 'architecture-diagram.png'")
    print("\n" + "=" * 70)

def generate_png():
    """Generate PNG from Mermaid markdown file"""
    
    print("🎨 Generating Architecture Diagram PNG...")
    print("=" * 70)
    
    # Check if mmdc is available
    if not check_mmdc_installed():
        install_mmdc()
        return False
    
    # Extract Mermaid code from markdown
    mermaid_code = []
    in_mermaid_block = False
    
    try:
        with open('architecture-diagram.md', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() == '```mermaid':
                    in_mermaid_block = True
                    continue
                elif line.strip() == '```' and in_mermaid_block:
                    break
                elif in_mermaid_block:
                    mermaid_code.append(line)
    except FileNotFoundError:
        print("❌ Error: architecture-diagram.md not found!")
        return False
    
    # Write temporary mermaid file
    with open('temp_diagram.mmd', 'w', encoding='utf-8') as f:
        f.writelines(mermaid_code)
    
    # Generate PNG with high quality settings
    try:
        print("\n🖼️  Rendering diagram with mmdc...")
        result = subprocess.run([
            'mmdc',
            '-i', 'temp_diagram.mmd',
            '-o', 'architecture-diagram.png',
            '-w', '2400',  # Width
            '-H', '1800',  # Height
            '-b', 'white',  # Background
            '-t', 'default',  # Theme
            '-s', '2'  # Scale factor for high DPI
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("\n✅ SUCCESS!")
            print("📍 Saved to: architecture-diagram.png")
            print("📏 Dimensions: 2400x1800px (High Resolution)")
            print("🎨 Ready for hackathon submission!")
            
            # Clean up temp file
            if os.path.exists('temp_diagram.mmd'):
                os.remove('temp_diagram.mmd')
            
            return True
        else:
            print(f"\n❌ Error generating PNG:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("\n❌ Timeout: Rendering took too long")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🌊 Ocean Forecasting Agent - Architecture Diagram Generator\n")
    
    success = generate_png()
    
    if not success:
        print("\n💡 ALTERNATIVE: Manual Export")
        print("   1. Open architecture-diagram.md in VS Code")
        print("   2. Install 'Markdown Preview Mermaid Support' extension")
        print("   3. Preview the diagram")
        print("   4. Take a screenshot or use online tool")
        print("\n   Online tool: https://mermaid.live/")
    
    print("\n" + "=" * 70)
