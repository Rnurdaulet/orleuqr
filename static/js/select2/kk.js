/*! Select2 4.1.0-rc.0 | https://github.com/select2/select2/blob/master/LICENSE.md */
!function () {
    if (jQuery && jQuery.fn && jQuery.fn.select2 && jQuery.fn.select2.amd) {
        var n = jQuery.fn.select2.amd;
        n.define("select2/i18n/kk", [], function () {
            function plural(n, one, few, many) {
                return n % 10 === 1 && n % 100 !== 11 ? one :
                       n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20) ? few : many;
            }

            return {
                errorLoading: function () {
                    return "Нәтижелерді жүктеу мүмкін емес";
                },
                inputTooLong: function (args) {
                    var overChars = args.input.length - args.maximum;
                    return "Өтінеміз, " + overChars + " таңбамен қысқартыңыз";
                },
                inputTooShort: function (args) {
                    var remainingChars = args.minimum - args.input.length;
                    return "Өтінеміз, тағы кемінде " + remainingChars + " таңба енгізіңіз";
                },
                loadingMore: function () {
                    return "Қосымша мәліметтер жүктелуде…";
                },
                maximumSelected: function (args) {
                    return "Сіз тек " + args.maximum + " элемент қана таңдай аласыз";
                },
                noResults: function () {
                    return "Нәтиже табылмады";
                },
                searching: function () {
                    return "Іздеу…";
                },
                removeAllItems: function () {
                    return "Барлық элементтерді өшіру";
                }
            };
        }), n.define, n.require;
    }
}();
