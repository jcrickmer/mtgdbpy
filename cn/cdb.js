$(function() { 
    window.cdb = {};
    cdb.init = function() {  
    };
    /**
     * predictes: an array of objects that have attributes 'field', 'op', and 'value'  
     * parent_jq: the results of a jQuery selector for the node in the dom where the results should be placed. E.g., $("#search_terms")
     **/
	cdb.searchPredicatesDisplay = function(predicates, parent_jq) {
		parent_jq.empty();
        for (var t = 0; t < predicates.length ; t++) {
            var rule = predicates[t];
			parent_jq.append($("<div>").append(rule.field + " :: " + rule.op + " :: \"" + rule.value + "\"")); 
		}
    }
}); 

$(function() {cdb.init();});
