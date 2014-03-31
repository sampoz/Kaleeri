$(function () {
    $('input[type=submit]').click(function (e) {
        e.preventDefault();
        var albumId = window.location.toString().split("/")[4];
        var order_id = $('#pid').val();
        var price = $('#price').val();
        var amount = $('#amount').val();

        $.getJSON('/order/checksum/' + order_id + '/' + price + '/' + amount + '/', function (data) {
            $('#checksum').val(data.checksum);
            $('#amount').val(parseInt($('#amount').val(), 10) * parseInt($('#price').val(), 10));
            $('form').submit();
        });
    });
});