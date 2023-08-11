ace.define("ace/mode/custom_sql", function(require, exports, module) {
    var oop = require("ace/lib/oop");
    var TextMode = require("ace/mode/text").Mode;
    var Tokenizer = require("ace/tokenizer").Tokenizer;
    var CustomSqlHighlightRules = require("ace/mode/custom_sql_highlight_rules").CustomSqlHighlightRules;

    var Mode = function() {
        this.HighlightRules = CustomSqlHighlightRules;
    };
    oop.inherits(Mode, TextMode);

    (function() {
        this.$id = "ace/mode/custom_sql";
    }).call(Mode.prototype);

    exports.Mode = Mode;
});

ace.define("ace/mode/custom_sql_highlight_rules", function(require, exports, module) {
    var oop = require("ace/lib/oop");
    var TextHighlightRules = require("ace/mode/text_highlight_rules").TextHighlightRules;

    var CustomSqlHighlightRules = function() {
        var keywords = "выбери|где|значение|изхранилища|обновить|положив|удалить|установить";  // Добавьте другие SQL ключевые слова, если нужно
        this.$rules = {
            "start" : [ {
                token : "keyword",
                regex : "\\b(?:" + keywords + ")\\b"
            }, {
                defaultToken : "text"
            }]
        };
    };

    oop.inherits(CustomSqlHighlightRules, TextHighlightRules);
    exports.CustomSqlHighlightRules = CustomSqlHighlightRules;
});
