$(function() { 
    window.cn = {};
    cn.cardstatsCache = {};
    cn.cardCache = {};
    cn.updateCard = function(targetId, multiverseId) {
		if (multiverseId === null) {
			return false;
		}
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
    cn.getCardStats = function(formatname, multiverseId) {
		var cardstats = window.cn.cardstatsCache[formatname + '-mvid-' + multiverseId];
		if (cardstats == null) {
			$.ajax({
				url: "/cards/_cardstats/" + formatname + '/mvid-' + multiverseId + "/",
				dataType: "json",
				async: false,
				complete: function(data) {
					var envelop = data.responseJSON;
					if (envelop.status == 'ok') {
						window.cn.cardstatsCache[formatname + '-mvid-' + multiverseId] = envelop.stats;
					}
					cardstats = envelop.stats;
				},
			});
		}
		return cardstats;
	};
    cn.getCardPrices = function(multiverseId, url_base, handler_func) {
        var cardprices;
        $.ajax({
                url: url_base + multiverseId,
                dataType: "json",
                async: true,
                handler_func: handler_func,
                complete: function(data) {
                    var envelop = data.responseJSON;
                    if (envelop.status == 'ok') {
                        if (window.cn.cardprices == null) {
                            window.cn.cardprices = envelop.cards;
                        } else {
                            for (var t = 0; t < envelop.cards.length; t++) {
                                window.cn.cardprices.push(envelop.cards[t]);
                            }
                        }
                    }
                    if (this.handler_func != null && typeof this.handler_func == "function") {
                        this.handler_func(window.cn.cardprices);
                    }
                }
            });
        return;
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
