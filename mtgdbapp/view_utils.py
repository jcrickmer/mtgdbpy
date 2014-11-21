from django.utils.safestring import mark_safe

def convertSymbolsToHTML(text):
	base = '/cn/glyphs/'
	tag_open = '<img src="/cn/glyphs/clear.png" ' + base
	tag_close = '>'
	result = text; #.lower()
	result = result.replace("{w}", tag_open + 'class="magic-symbol-small symbol_mana_w_small" alt="{w}"' + tag_close)
	result = result.replace("{u}", tag_open + 'class="magic-symbol-small symbol_mana_u_small" alt="{u}"' + tag_close)
	result = result.replace("{b}", tag_open + 'class="magic-symbol-small symbol_mana_b_small" alt="{b}"' + tag_close)
	result = result.replace("{r}", tag_open + 'class="magic-symbol-small symbol_mana_r_small" alt="{r}"' + tag_close)
	result = result.replace("{g}", tag_open + 'class="magic-symbol-small symbol_mana_g_small" alt="{g}"' + tag_close)

	result = result.replace("{wp}", tag_open + 'class="magic-symbol-small symbol_mana_wp_small" alt="{wp}"' + tag_close)
	result = result.replace("{up}", tag_open + 'class="magic-symbol-small symbol_mana_up_small" alt="{up}"' + tag_close)
	result = result.replace("{bp}", tag_open + 'class="magic-symbol-small symbol_mana_bp_small" alt="{bp}"' + tag_close)
	result = result.replace("{rp}", tag_open + 'class="magic-symbol-small symbol_mana_rp_small" alt="{rp}"' + tag_close)
	result = result.replace("{gp}", tag_open + 'class="magic-symbol-small symbol_mana_gp_small" alt="{gp}"' + tag_close)

	result = result.replace("{2w}", tag_open + 'class="magic-symbol-small symbol_mana_2w_small" alt="{2w}"' + tag_close)
	result = result.replace("{2u}", tag_open + 'class="magic-symbol-small symbol_mana_2u_small" alt="{2u}"' + tag_close)
	result = result.replace("{2b}", tag_open + 'class="magic-symbol-small symbol_mana_2b_small" alt="{2b}"' + tag_close)
	result = result.replace("{2r}", tag_open + 'class="magic-symbol-small symbol_mana_2r_small" alt="{2r}"' + tag_close)
	result = result.replace("{2g}", tag_open + 'class="magic-symbol-small symbol_mana_2g_small" alt="{2g}"' + tag_close)

	result = result.replace("{wu}", tag_open + 'class="magic-symbol-small symbol_mana_wu_small" alt="{wu}"' + tag_close)
	result = result.replace("{wb}", tag_open + 'class="magic-symbol-small symbol_mana_wb_small" alt="{wb}"' + tag_close)
	result = result.replace("{ub}", tag_open + 'class="magic-symbol-small symbol_mana_ub_small" alt="{ub}"' + tag_close)
	result = result.replace("{ur}", tag_open + 'class="magic-symbol-small symbol_mana_ur_small" alt="{ur}"' + tag_close)
	result = result.replace("{br}", tag_open + 'class="magic-symbol-small symbol_mana_br_small" alt="{br}"' + tag_close)

	result = result.replace("{bg}", tag_open + 'class="magic-symbol-small symbol_mana_bg_small" alt="{bg}"' + tag_close)
	result = result.replace("{rg}", tag_open + 'class="magic-symbol-small symbol_mana_rg_small" alt="{rg}"' + tag_close)
	result = result.replace("{rw}", tag_open + 'class="magic-symbol-small symbol_mana_rw_small" alt="{rw}"' + tag_close)
	result = result.replace("{gw}", tag_open + 'class="magic-symbol-small symbol_mana_gw_small" alt="{gw}"' + tag_close)
	result = result.replace("{gu}", tag_open + 'class="magic-symbol-small symbol_mana_gu_small" alt="{gu}"' + tag_close)

	result = result.replace("{x}", tag_open + 'class="magic-symbol-small symbol_mana_x_small" alt="{x}"' + tag_close)
	result = result.replace("{p}", tag_open + 'class="magic-symbol-small symbol_phyrexian_small" alt="{p}"' + tag_close)
	result = result.replace("{t}", tag_open + 'class="magic-symbol-small symbol_tap_small" alt="{t}"' + tag_close)
	result = result.replace("{q}", tag_open + 'class="magic-symbol-small symbol_untap_small" alt="{q}"' + tag_close)
	result = result.replace("{untap}", tag_open + 'class="magic-symbol-small symbol_untap_small" alt="{q}"' + tag_close)

	# ####
	result = result.replace("{W}", tag_open + 'class="magic-symbol-small symbol_mana_w_small" alt="{w}"' + tag_close)
	result = result.replace("{U}", tag_open + 'class="magic-symbol-small symbol_mana_u_small" alt="{u}"' + tag_close)
	result = result.replace("{B}", tag_open + 'class="magic-symbol-small symbol_mana_b_small" alt="{b}"' + tag_close)
	result = result.replace("{R}", tag_open + 'class="magic-symbol-small symbol_mana_r_small" alt="{r}"' + tag_close)
	result = result.replace("{G}", tag_open + 'class="magic-symbol-small symbol_mana_g_small" alt="{g}"' + tag_close)

	result = result.replace("{WP}", tag_open + 'class="magic-symbol-small symbol_mana_wp_small" alt="{wp}"' + tag_close)
	result = result.replace("{UP}", tag_open + 'class="magic-symbol-small symbol_mana_up_small" alt="{up}"' + tag_close)
	result = result.replace("{BP}", tag_open + 'class="magic-symbol-small symbol_mana_bp_small" alt="{bp}"' + tag_close)
	result = result.replace("{RP}", tag_open + 'class="magic-symbol-small symbol_mana_rp_small" alt="{rp}"' + tag_close)
	result = result.replace("{GP}", tag_open + 'class="magic-symbol-small symbol_mana_gp_small" alt="{gp}"' + tag_close)

	result = result.replace("{2W}", tag_open + 'class="magic-symbol-small symbol_mana_2w_small" alt="{2w}"' + tag_close)
	result = result.replace("{2U}", tag_open + 'class="magic-symbol-small symbol_mana_2u_small" alt="{2u}"' + tag_close)
	result = result.replace("{2B}", tag_open + 'class="magic-symbol-small symbol_mana_2b_small" alt="{2b}"' + tag_close)
	result = result.replace("{2R}", tag_open + 'class="magic-symbol-small symbol_mana_2r_small" alt="{2r}"' + tag_close)
	result = result.replace("{2G}", tag_open + 'class="magic-symbol-small symbol_mana_2g_small" alt="{2g}"' + tag_close)

	result = result.replace("{WU}", tag_open + 'class="magic-symbol-small symbol_mana_wu_small" alt="{wu}"' + tag_close)
	result = result.replace("{WB}", tag_open + 'class="magic-symbol-small symbol_mana_wb_small" alt="{wb}"' + tag_close)
	result = result.replace("{UB}", tag_open + 'class="magic-symbol-small symbol_mana_ub_small" alt="{ub}"' + tag_close)
	result = result.replace("{UR}", tag_open + 'class="magic-symbol-small symbol_mana_ur_small" alt="{ur}"' + tag_close)
	result = result.replace("{BR}", tag_open + 'class="magic-symbol-small symbol_mana_br_small" alt="{br}"' + tag_close)
	result = result.replace("{BG}", tag_open + 'class="magic-symbol-small symbol_mana_bg_small" alt="{bg}"' + tag_close)
	result = result.replace("{RG}", tag_open + 'class="magic-symbol-small symbol_mana_rg_small" alt="{rg}"' + tag_close)
	result = result.replace("{RW}", tag_open + 'class="magic-symbol-small symbol_mana_rw_small" alt="{rw}"' + tag_close)
	result = result.replace("{GW}", tag_open + 'class="magic-symbol-small symbol_mana_gw_small" alt="{gw}"' + tag_close)
	result = result.replace("{GU}", tag_open + 'class="magic-symbol-small symbol_mana_gu_small" alt="{gu}"' + tag_close)

	result = result.replace("{X}", tag_open + 'class="magic-symbol-small symbol_mana_x_small" alt="{x}"' + tag_close)
	result = result.replace("{P}", tag_open + 'class="magic-symbol-small symbol_mana_phyrexian_small" alt="{p}"' + tag_close)
	result = result.replace("{T}", tag_open + 'class="magic-symbol-small symbol_tap_small" alt="{t}"' + tag_close)
	result = result.replace("{Q}", tag_open + 'class="magic-symbol-small symbol_untap_small" alt="{q}"' + tag_close)
	result = result.replace("{UNTAP}", tag_open + 'class="magic-symbol-small symbol_untap_small" alt="{q}"' + tag_close)
	# ####

	for x in range(0, 15):
		result = result.replace("{" + str(x) + "}", tag_open + ' class="magic-symbol-small symbol_mana_' + str(x) + '_small" alt="{' + str(x) + '}"' + tag_close)

	result = result.replace("\n", "<br />\n")

	return mark_safe(result)
