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
    cn.getCardPrices = function(multiverseId, url_base, auth_key, handler_func) {
        var call_url = url_base.concat(multiverseId);
        if (call_url.indexOf("?") < 0) {
            call_url = call_url + "?";
        } else {
            call_url = call_url + "&";
        }
        call_url = call_url + "key=" + auth_key;
        $.ajax({
                url: call_url,
                dataType: "json",
                async: true,
                handler_func: handler_func,
                complete: function(data) {
                    var envelop = data.responseJSON;
                    if (envelop.status.toLowerCase() == 'ok') {
                        if (window.cn.cardprices == null) {
                            window.cn.cardprices = new Array();
                        }
                        // Could be one of two formats. First, check Deckbox format...
                        if (envelop.prices && envelop.prices instanceof Array) {
                            // each item in the array should be like this:
                            // {"mvid": 9999999, "setname": "xxxxx", "normalprice": 99.99, "normalsale": 0|1, "foil": 999.99, "foilsale": 0|1}
                            for (var qq = 0 ; qq < envelop.prices.length ; qq++) {
                                mcard = {};
                                mcard["name"] = envelop.name;
                                mcard["price"] = envelop.prices[qq].normalprice;
                                mcard["on_sale"] = envelop.prices[qq].normalsale == 1;
                                mcard["mvid"] = envelop.prices[qq].mvid;
                                mcard["printing"] = "normal"
                                mcard["expansionset"] = {"name": envelop.prices[qq].setname}
                                window.cn.cardprices.push(mcard);
                                if ((envelop.prices[qq].foil || envelop.prices[qq].foilprice) && (envelop.prices[qq].foil > 0 || envelop.prices[qq].foilprice > 0)) {
                                    fcard = {};
                                    fcard["name"] = envelop.name;
                                    fcard["price"] = envelop.prices[qq].foil || envelop.prices[qq].foilprice;
                                    fcard["on_sale"] = envelop.prices[qq].foilsale == 1;
                                    fcard["mvid"] = envelop.prices[qq].mvid;
                                    fcard["printing"] = "foil"
                                    fcard["expansionset"] = {"name": envelop.prices[qq].setname}
                                    window.cn.cardprices.push(fcard);
                                }
                            }
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
