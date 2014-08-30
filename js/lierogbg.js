'use strict';
function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+-)');
    var replacement = prefix + '-' + ndx + '-';
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex,
    replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function deleteForm(btn, prefix) {
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
    return false;
}

function addForm(btn, prefix) {
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

        // Add an event handler for the delete item/form link
        $(row).find(".delete_form").click(function () {
            return deleteForm(this, prefix);
        });

        // Update the total form count
        $("#id_" + prefix + "-TOTAL_FORMS").val(formCount + 1);
    }
    return false;
}

$(document).ready(function () {
    // Register the click event handlers
    $("#add_subgame_form").click(function () {
        return addForm(this, "subgame_set");
    });

    $(".delete_subgame_form").click(function () {
        return deleteForm(this, "subgame_set");
    });
});
