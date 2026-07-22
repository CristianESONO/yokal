#!/usr/bin/env python3
import re

# Read the file
with open('/usr/local/etc/yokal/templates/dashboard/settings.html', 'r', encoding='utf-8') as f:
    content = f.read()

# New card preview HTML
new_card = '''      <!-- Preview Card - New Design -->
      <div id="preview-card" class="relative w-full aspect-[5/3] rounded-[2rem] p-7 flex flex-col text-white overflow-hidden shadow-[0_30px_80px_-20px_rgba(15,23,42,0.5)] ring-1 ring-white/10 transition-all duration-300"
           style="background: radial-gradient(120% 120% at 0% 0%, {{ program.color_secondary|default:program.color_primary|default:'#f59e0b' }}22 0%, transparent 45%), radial-gradient(120% 120% at 100% 100%, {{ program.color_secondary|default:program.color_primary|default:'#f59e0b' }}18 0%, transparent 50%), linear-gradient(135deg, {{ program.color_primary|default:'#0f172a' }} 0%, #1e293b 100%);">
        
        <!-- Décor / reflets -->
        <div class="pointer-events-none absolute inset-0">
          <div class="absolute -top-24 -right-16 w-72 h-72 rounded-full bg-white/5 blur-3xl"></div>
          <div class="absolute -bottom-32 -left-20 w-80 h-80 rounded-full blur-3xl" style="background-color: {{ program.color_secondary|default:program.color_primary|default:'#f59e0b' }}22"></div>
          <div class="absolute inset-0 opacity-[0.06] mix-blend-overlay" style="background-image: radial-gradient(rgba(255,255,255,0.9) 1px, transparent 1px); background-size: 4px 4px;"></div>
        </div>

        <!-- Standard Layer -->
        <div id="standard-preview-layer" class="h-full flex flex-col {% if program.use_custom_design %}hidden{% endif %}">
          <!-- Ligne logo + marque -->
          <div class="relative flex items-start justify-between">
            <div class="flex items-center gap-4">
              <div class="w-24 h-24 rounded-3xl bg-gradient-to-br from-white to-neutral-100 border border-white/40 flex items-center justify-center overflow-hidden flex-shrink-0 shadow-[0_10px_30px_-10px_rgba(0,0,0,0.4)]">
                {% if user.merchant_profile.logo %}
                  <img id="logo-preview" src="{{ user.merchant_profile.logo.url }}" class="w-full h-full object-contain">
                {% else %}
                  <span id="logo-initial" class="text-5xl font-black tracking-tight" style="color: {{ program.color_primary|default:'#0f172a' }}">
                    {{ user.merchant_profile.business_name|first }}
                  </span>
                {% endif %}
              </div>
              <div>
                <div class="text-[10px] uppercase tracking-[0.25em] text-white/50 font-semibold flex items-center gap-1.5">
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20" style="color: {{ program.color_secondary|default:program.color_primary|default:'#f59e0b' }}"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                  Membre privilégié
                </div>
                <div id="preview-biz-name" class="font-serif text-2xl leading-tight mt-1">{{ user.merchant_profile.business_name }}</div>
                <div class="text-[11px] text-white/40 tracking-wider mt-0.5">Loyalty · No. 0042</div>
              </div>
            </div>

            <div class="text-right">
              <div class="text-[9px] uppercase tracking-[0.2em] text-white/40">Devise</div>
              <div class="text-lg font-semibold mt-0.5" style="color: {{ program.color_secondary|default:program.color_primary|default:'#f59e0b' }}">
                {% if program.currency == 'EUR' %}€{% elif program.currency == 'USD' %}${% else %}FCFA{% endif %}
              </div>
            </div>
          </div>

          <!-- Barre de progression -->
          <div class="relative mt-auto">
            <div class="flex items-center justify-between mb-2">
              <div class="text-[10px] uppercase tracking-[0.25em] text-white/50 font-semibold">
                Progression
              </div>
              <div class="text-[11px] text-white/70 font-mono tabular-nums">
                3/10
              </div>
            </div>
            <div class="flex gap-1.5">
              {% for i in "1234567891"|make_list %}
              <div class="flex-1 h-2 rounded-full overflow-hidden bg-white/10 backdrop-blur">
                <div class="h-full rounded-full transition-all" style="width: {% if forloop.counter <= 3 %}100%{% else %}0%{% endif %}; background: linear-gradient(90deg, {{ program.color_secondary|default:program.color_primary|default:'#f59e0b' }}, #fbbf24); box-shadow: {% if forloop.counter <= 3 %}0 0 12px {{ program.color_secondary|default:program.color_primary|default:'#f59e0b' }}99{% endif %};"></div>
              </div>
              {% endfor %}
            </div>
          </div>

          <!-- Pastille récompense -->
          <div class="relative mt-4 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center border border-white/15" style="background: {{ program.color_secondary|default:program.color_primary|default:'#f59e0b' }}22">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: {{ program.color_secondary|default:program.color_primary|default:'#f59e0b' }}"><path d="M18 8h1a4 4 0 010 8h-1M2 8h16v9a4 4 0 01-4 4H6a4 4 0 01-4-4V8z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 1v3M10 1v3M14 1v3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </div>
              <div>
                <div class="text-[9px] uppercase tracking-[0.2em] text-white/40">
                  Récompense
                </div>
                <div id="preview-reward" class="text-sm font-semibold">{{ program.reward_description|default:"1 café offert" }}</div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-[9px] uppercase tracking-[0.2em] text-white/40">Valide</div>
              <div class="text-xs font-mono text-white/70">12 / 26</div>
            </div>
          </div>
        </div>

        <!-- Custom Layer -->
        <div id="custom-preview-layer" class="h-full {% if not program.use_custom_design %}hidden{% endif %}">
          <!-- Dynamically filled -->
        </div>

      </div>'''

# Pattern to match the old card preview section (from <!-- Preview Card - New Design --> to </div> before mt-8)
pattern = r'<!-- Preview Card - New Design -->.*?(?=\n      <div class="mt-8 space-y-4">)'

# Replace
content = re.sub(pattern, new_card.strip(), content, flags=re.DOTALL)

# Write back
with open('/usr/local/etc/yokal/templates/dashboard/settings.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Card preview replaced successfully!")
