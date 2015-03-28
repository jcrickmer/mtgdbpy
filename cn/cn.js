$(function() { 
    window.cn = {};
    cn.cardCache = {};
    cn.updateCard = function(targetId, multiverseId) {  
		var card = cn.getCard(multiverseId);
		var result = "<img src=\"" + card.img_url + "\" class=\"card\" alt=\""+ card.name + "\">";
		result += "<div>" + card.name + "</div>";
		result += "<div>" + card.mana_cost_html + "</div>";
		result += "<div>" + card.text + "</div>";
		$("#" + targetId).html(result);
		return true;
	};
    cn.getCard = function(multiverseId) {
		var card = window.cn.cardCache['mid' + multiverseId];
		if (card == null) {
			$.ajax({
				url: "/cards/" + multiverseId + "/",
				dataType: "json",
				async: false,
				complete: function(data) {
					var envelop = data.responseJSON;
					if (envelop.status == 'success') {
						window.cn.cardCache['mid' + multiverseId] = envelop.cards[0]; // hard coded to the first result that comes back.
					}
					card = envelop.cards[0]; // hard coded to the first result that comes back.
				},
			});
		}
		return card;
	};
    cn.initToolTips = function() {  
        $(document).uitooltip({
            items: "[data-mid]", 
            tooltipClass:'preview-tip', 
            content: function(callback) {  
                var element = $(this);
				var dataMid = element.attr("data-mid");
				var result = "waiting...";
				var card = cn.getCard(dataMid);
				result = "<img src=\"" + card.img_url + "\" class=\"card\" alt=\""+ card.name + "\">";
				return result;
            }
        });
    };  
    cn.init = function() {  
        cn.initToolTips(); 
    }; 
}); 

$(function() {cn.init();});
