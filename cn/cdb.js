$(function() { 
    window.cdb = {};
    cdb.init = function() {  
    };
	cdb.predicates = {};
    /**
     * predictes: an array of objects that have attributes 'field', 'op', 'value', and 'hint'
     * parent_jq: the string that you would pass to a jQuery selector for the node in the dom where the results should be placed. E.g., "#search_terms"
     **/
	cdb.searchPredicatesDisplay = function(predicates, parent_jqs, doNotShowRemove) {
		cdb.predicates = predicates;
		parent_jq = $(parent_jqs);
		parent_jq.empty();
        for (var t = 0; t < predicates.length ; t++) {
            var rule = predicates[t];
			var result = rule.field;
			if (rule.field == "format") {
				result = result + " is \"" + rule.value + "\"";
			} else if (rule.op == "and") {
				result = result + " contains \"" + rule.value + "\"";
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
			if (doNotShowRemove) {
				parent_jq.append($("<div>").append(result));
			} else {
				parent_jq.append($("<div>").append(result, "<a class=\"pred_remove\" href=\"#\" onclick=\"cdb.removeSearchPredicate('" + rule.hint + "','" + parent_jqs + "');\">x</a>")); 
			}
		}
    };
	cdb.removeSearchPredicate = function(hint, parent_jqs) {
		for (var h = 0 ; h < cdb.predicates.length ; h++) {
			var pred = cdb.predicates[h];
			if (pred.hint == hint) {
				// remove it
				cdb.predicates.splice(h, 1);
				break;
  			}
		}
		cdb.searchPredicatesDisplay(cdb.predicates, parent_jqs);
		return false;
	};
}); 

$(function() {cdb.init();});
