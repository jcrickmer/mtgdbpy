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
                      'power':'Power',
                      'toughness':'Toughness',
                      'similar':'Similar',
                      'supertype':'Supertype',
                      'type':'Type',
                      'subtype':'Subtype',
                      'ispermanent':'Permanent',
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
            } else if (rule.field == "similar") {
                result = result + " to \"" + rule.value + "\"";
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
                if (rule.field == "color") {
                    result = result + " is not " + cdb.colors[rule.value];
                } else if (rule.field == "rarity") {
                    result = result + " is not " + cdb.rarities[rule.value];
                } else {
		    result = result + " does not contain \"" + rule.value + "\"";
		}
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
            resButton_html = resButton_html + cdb.cleanHint(rule.hint) + "','" + parent_jqs + "'";
            if (autoSearchOnRemove) {
                resButton_html = resButton_html + ',true';
            } else {
                resButton_html = resButton_html + ',false';
            }
            resButton_html = resButton_html + ");\">" + result + "&nbsp;<span class=\"glyphicon glyphicon-align-right glyphicon-remove-sign\"></span></button>";
            parent_jq.append($(childTag).append(resButton_html));
        }
    };
    cdb.cleanHint = function(hint) {
        return hint.replace(/[^a-zA-Z0-9_{}]/, "_");
    };
    cdb.removeSearchPredicate = function(hint, parent_jqs, autoSubmitQuery) {
        //console.log("trying to remove hint\"" + hint + "\"")
        for (var h = 0 ; h < cdb.predicates.length ; h++) {
            var pred = cdb.predicates[h];
            if (cdb.cleanHint(pred.hint) == cdb.cleanHint(hint)) {
                // remove it
                cdb.predicates.splice(h, 1);
                break;
              }
        }
        if (autoSubmitQuery) {
	    // We need to force the query to go back to the main search. Why? Because we don't want to have removed search preidcates masquaring around on pages like 'abzan-commanders', because then it wouldn't be abzan-commanders any more, would it?
            cdb.sendQuery('/cards/_search');
        } else {
            cdb.searchPredicatesDisplay(cdb.predicates, parent_jqs);
        }
        return false;
    };
    cdb.sort = undefined;
    cdb.sendQuery = function(action_loc) {
	if (action_loc == null) {
            action_loc = window.location.href.split('?')[0];
	    if (action_loc.endsWith('cards/')) {
	        action_loc = '_search';
	    }
	}
        var form_jq = $("<form action=\"" + action_loc + "\" method=\"get\">");
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
    cdb.name_to_url_map = {};
    cdb.getCardNames = function(request, response) {
        $.ajax({
            url: "/cards/_nameauto/",
            dataType: "jsonp",
            data: {
                q: request.term
            },
            success: function( data ) {
                vals = new Array()
                for(var cc = 0; cc < data.length; cc++) {
                  vals.push(data[cc]['name'])
                  cdb.name_to_url_map[data[cc]['name']] = data[cc]['url'];
                }
                response(vals);
            }
        });
    };
    cdb.STAY_ON_PAGE = false;
    cdb.AUTO_NAVIGATE = true;
    cdb.makeFieldNameAuto = function(jqObj, navigationOption) {
        /* Makes the given form field identified by the JQuery object into an autocomplete field for card names. */
        jqObj.autocomplete({
            source: cdb.getCardNames,
            minLength: 3,
            select: function( event, ui ) {
                if (navigationOption) {
                    dataLayer.push({'event':'tutor',
                                    'eventCategory': 'navigation',
			                        'eventAction': 'select',
			                        'eventValue': cdb.name_to_url_map[ui.item.label],});
                    // Just go directly to that page
                    window.location.href = cdb.name_to_url_map[ui.item.label];
                }
            },
            open: function() {
                $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
            },
            close: function() {
                $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
            }
        });
    };
});

$(function() {cdb.init();});
