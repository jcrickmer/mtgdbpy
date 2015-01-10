$(function() { 
    window.cdb = {};
    cdb.init = function() {
    };
    cdb.colors = {"w":"White","u":"Blue","b":"Black","r":"Red","g":"Green","c":"Colorless"};
    cdb.rarities = {'b':'Basic Land',
                    'c':'Common',
                    'm':'Mythic Rare',
                    'r':'Rare',
                    's':'Special',
                    'u':'Uncommon',
                   };
    cdb.fieldNames = {'cardname':'Name',
                      'rules':'Rules Text',
                      'color':'Color',
                      'cmc':'CMC',
                      'type':'Type',
                      'subtype':'Subtype',
                      'rarity':'Rarity',
                      'format':'Format',
                     };
	cdb.predicates = {};
    /**
     * predictes: an array of objects that have attributes 'field', 'op', 'value', and 'hint'
     * parent_jq: the string that you would pass to a jQuery selector for the node in the dom where the results should be placed. E.g., "#search_terms"
     **/
	cdb.searchPredicatesDisplay = function(predicates, parent_jqs, autoSearchOnRemove) {
		cdb.predicates = predicates;
		parent_jq = $(parent_jqs);
		childTag = "<div>";
		if (parent_jq.prop("tagName") == "UL") {
			childTag = "<li>";
		}
		parent_jq.empty();
        for (var t = 0; t < predicates.length ; t++) {
            var rule = predicates[t];
			var result = cdb.fieldNames[rule.field];
			if (rule.field == "format") {
				result = result + " is \"" + rule.value + "\"";
			} else if (rule.op == "and") {
				result = result + " contains ";
                if (rule.field == "color") {
                    result = result + cdb.colors[rule.value];
                } else if (rule.field == "rarity") {
                    result = result + cdb.rarities[rule.value];
                } else { 
                    result = result + "\"" + rule.value + "\"";
                }
			} else if (rule.op == "or") { /* revisit this one */
				result = result + " contains ";
                if (rule.field == "color") {
                    result = result + cdb.colors[rule.value];
                } else if (rule.field == "rarity") {
                    result = result + cdb.rarities[rule.value];
                } else { 
                    result = result + "\"" + rule.value + "\"";
                }
			} else if (rule.op == "not") {
				result = result + " does not contain \"" + rule.value + "\"";
			} else if (rule.op == "eq") {
				result = result + " = " + rule.value;
			} else if (rule.op == "ne") {
				result = result + " != " + rule.value;
			} else if (rule.op == "lt") {
				result = result + " &lt; " + rule.value;
			} else if (rule.op == "gt") {
				result = result + " &gt; " + rule.value;
			}
            var resButton_html = "<button class=\"btn btn-default\" onclick=\"cdb.removeSearchPredicate('";
            resButton_html = resButton_html + rule.hint + "','" + parent_jqs + "'";
			if (autoSearchOnRemove) {
				resButton_html = resButton_html + ',true';
            } else {
				resButton_html = resButton_html + ',false';
            }
            resButton_html = resButton_html + ");\">" + result + "&nbsp;<span class=\"glyphicon glyphicon-align-right glyphicon-remove-sign\"></span></button>";
			parent_jq.append($(childTag).append(resButton_html));
		}
    };
	cdb.removeSearchPredicate = function(hint, parent_jqs, autoSubmitQuery) {
		for (var h = 0 ; h < cdb.predicates.length ; h++) {
			var pred = cdb.predicates[h];
			if (pred.hint == hint) {
				// remove it
				cdb.predicates.splice(h, 1);
				break;
  			}
		}
		if (autoSubmitQuery) {
            cdb.sendQuery();
        } else {
            cdb.searchPredicatesDisplay(cdb.predicates, parent_jqs);
        }
		return false;
	};
    cdb.sort = undefined;
    cdb.sendQuery = function() {
        var form_jq = $("<form action=\"_search\" method=\"get\">");
        $(document.body).append(form_jq);
        form_jq.append("<input id=\"subform_q\" type=\"hidden\" name=\"query\">");
        $("#subform_q").val(JSON.stringify(window.predicates));
        if (cdb.sort != null) {
            form_jq.append("<input id=\"subform_s\" type=\"hidden\" name=\"sort\">");
            $("#subform_s").val(cdb.sort);
        }
        form_jq.submit();
        return false; //event.preventDefault();
    };
});

$(function() {cdb.init();});
