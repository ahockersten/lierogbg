'use strict';
function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+-)');
    var replacement = prefix + '-' + ndx + '-';
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex,
    replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function deleteSubgameForm(btn, prefix) {
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (formCount > 1) {
        // Delete the item/form
        $(btn).parents('.subgame_item').remove();
        var forms = $('.subgame_item'); // Get all the forms
        // Update the total number of forms (1 less than before)
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        formCount = forms.length;
        // Go through the forms and set their indices, names and IDs
        for (var i = 0; i < formCount; i++) {
            $(forms.get(i)).find("*").each(function () {
                updateElementIndex(this, prefix, i);
            });
        }
    }
    $(".add_subgame_form:last").show()
    return false;
}

function addSubgameForm(btn, prefix) {
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    // You can only submit a maximum of 10 subgames
    if (formCount < 10) {
        // Clone a form (without event handlers) from the last
        var row = $(".subgame_item:first").clone(false).get(0);
        // Insert it after the last form
        $(row).removeAttr('id').hide().insertAfter(".subgame_item:last").slideDown(300);

        // Remove the bits we don't want in the new row/form
        // e.g. error messages
        $(".errorlist", row).remove();
        $(row).children().removeClass("error");

        // Relabel or rename all the relevant bits
        $(row).find("*").each(function () {
            updateElementIndex(this, prefix, formCount);
            $(this).val("");
        });

        // Add an event handler for the add item/form link
        $(row).find(".add_subgame_form").click(function () {
            return addSubgameForm(this, prefix);
        });

        // Add an event handler for the delete item/form link
        $(row).find(".delete_subgame_form").click(function () {
            return deleteSubgameForm(this, prefix);
        });

        // Update the total form count
        $("#id_" + prefix + "-TOTAL_FORMS").val(formCount + 1);

        // scroll to the top of the new form
        $('html, body').animate({scrollTop: $(row).offset().top});
        $(".add_subgame_form").each(function(index) {
            $(this).hide();
        });
        $(".add_subgame_form:last").show()
    }
    return false;
}

function shadeColor(color, percent) {
    var f=parseInt(color.slice(1),16),t=percent<0?0:255,p=percent<0?percent*-1:percent,R=f>>16,G=f>>8&0x00FF,B=f&0x0000FF;
    return "#"+(0x1000000+(Math.round((t-R)*p)+R)*0x10000+(Math.round((t-G)*p)+G)*0x100+(Math.round((t-B)*p)+B)).toString(16).slice(1);
}

function blendColors(c0, c1, p) {
    var f=parseInt(c0.slice(1),16),t=parseInt(c1.slice(1),16),R1=f>>16,G1=f>>8&0x00FF,B1=f&0x0000FF,R2=t>>16,G2=t>>8&0x00FF,B2=t&0x0000FF;
    return "#"+(0x1000000+(Math.round((R2-R1)*p)+R1)*0x10000+(Math.round((G2-G1)*p)+G1)*0x100+(Math.round((B2-B1)*p)+B1)).toString(16).slice(1);
}

function update_images() {
    var lieroworm_left = "/static/img/lieroworm_pointing_left.svg"
    var lieroworm_right = "/static/img/lieroworm_pointing_right.svg"
    $.get(lieroworm_left, function(data) {
        // Get the SVG tag, ignore the rest
        var svg = $(data).find('svg');
        // Remove any invalid XML tags as per http://validator.w3.org
        svg = svg.removeAttr('xmlns:a');
        $(".lieroworm_left").each(function(index) {
            var img = $(this);
            var imgID = img.attr('id');
            var imgClass = img.attr('class');
            var imgURL = img.attr('src');

            var clone = svg.clone();
            // Replace image with new SVG
            img.replaceWith(clone);

            var color = $(this).attr('id');
            clone.find("#svg_light_color").each(function(index) {
                $(this).css({'fill' : shadeColor(color, -0.2)});
            });
            clone.find("#svg_medium_color").each(function(index) {
                $(this).css({'fill' : color});
            });
            clone.find("#svg_dark_color").each(function(index) {
                $(this).css({'fill' : shadeColor(color, 0.2)});
            });
        });
    }, 'xml');
    $.get(lieroworm_right, function(data) {
        // Get the SVG tag, ignore the rest
        var svg = $(data).find('svg');
        // Remove any invalid XML tags as per http://validator.w3.org
        svg = svg.removeAttr('xmlns:a');
        $(".lieroworm_right").each(function(index) {
            var img = $(this);
            var imgID = img.attr('id');
            var imgClass = img.attr('class');
            var imgURL = img.attr('src');

            var clone = svg.clone();
            // Replace image with new SVG
            img.replaceWith(clone);

            var color = $(this).attr('id');
            clone.find("#svg_light_color").each(function(index) {
                $(this).css({'fill' : shadeColor(color, -0.2)});
            });
            clone.find("#svg_medium_color").each(function(index) {
                $(this).css({'fill' : color});
            });
            clone.find("#svg_dark_color").each(function(index) {
                $(this).css({'fill' : shadeColor(color, 0.2)});
            });
        });
    }, 'xml');
}

$(document).ready(function () {
    // Register the click event handlers
    $(".add_subgame_form").click(function () {
        return addSubgameForm(this, "subgame_set");
    });

    $(".delete_subgame_form").click(function () {
        return deleteSubgameForm(this, "subgame_set");
    });

    $('.datepicker-input').datetimepicker({
        format: "YYYY-MM-DD HH:mm",
        defaultDate: moment(),
        sideBySide: true,
        locale: moment.locale(window.navigator.userLanguage ||
                              window.navigator.language),
    });

    update_images();
});
