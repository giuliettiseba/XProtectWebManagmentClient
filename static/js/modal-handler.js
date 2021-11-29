$('.btn').on('click', function (event) {
    event.preventDefault(); // To prevent following the link (optional)
    console.log(this.id)
    switch (this.id) {
        case 'AddCameraGroup':
            create_modal(
                'Add Camera Group',
                {'name': 'text', 'description': 'text'},
                {'Save': add_camera_group_save, 'Delete': remove_camera_group_save, 'Close': cancel_action}
            )
            show_modal()
            break;
        default:
            console.log(`Sorry, cannot start task ${this.id}.`);
    }
});

show_modal = function () {
    $('#myModal').modal('show')
}

hide_modal = function () {
    $('#myModal').modal('hide')
}

destroy_modal = function () {
    $('#modalPlaceholder').html('')
}


// Dynamically create a modal to show the array of properties to be filled
add_camera_group_save = function () {
    const form_values = $("#target").serializeArray()
    const modal_body = $('.modal-body').html('')
    const modal_footer = $('.modal-footer').html('')
    const modal_header = $('.modal-header').html('')


    $.post('/cameraGroups/AddCameraGroup', {name: form_values[0].value, description: form_values[1].value},
        function (returnedData) {
            if (returnedData['errorCode'] == 200) {
                modal_header.css('background-color', '#ADFF2F').html('<h5 class="modal-title" id="exampleModalLabel">Success</h5>')

                $('<div>', {
                    text: 'Camera Group Added'
                }).appendTo(modal_body)

            } else {
                modal_header.css('background-color', '#B22222').html('<h5 class="modal-title" id="exampleModalLabel">Error</h5>')
                for (const [key, value] of Object.entries(returnedData)) {
                    $('<div>', {
                        text: value
                    }).appendTo(modal_body)
                }
            }
        })

    modal_footer.append($('<button/>', {
        text: 'Close',
        type: 'button',
        class: 'btn btn-secondary',
        click: cancel_action
    }));

    $('#myModal').modal('handleUpdate')
}

remove_camera_group_save = function () {
    console.log("im going im going")
}

cancel_action = function () {
    hide_modal()
    destroy_modal();
}

// Create a model with the passed parameters
// title: modal title
// fields: dictionary with the key as the field and the value as the type (Text or boolean)
// buttons: Button nama as the key and function as value
function create_modal(title, fields, buttons) {
    $('#modalPlaceholder').html('')

    const modal_fade = $('<div>', {
        'class': 'modal fade',
        'id': 'myModal',
        'tabindex': '-1',
        'role': 'dialog',
        'aria': 'exampleModalLabel',
        'aria-hidden': 'true',
    })

    const modal_dialog = $('<div>', {
        //<div
        // class="modal-dialog" role="document">
        'class': 'modal-dialog',
        'role': 'document'
    }).appendTo(modal_fade)

    const modal_content = $('<div>', {
        'class': 'modal-content'
    }).appendTo(modal_dialog)

    const modal_header = $('<div>', {
        'class': 'modal-header'
    }).appendTo(modal_content)

    const modal_title = $('<h5>', {
        'class': 'modal-title',
        'id': "ModalLabel",
        'text': title
    }).appendTo(modal_header)


    const modal_body = $('<div>', {
        'class': 'modal-body'
    }).appendTo(modal_content)

    const form_group = $('<div>', {
        class: 'form-group',
    }).appendTo(modal_body);

    const newForm = $('<form>', {
        'id': "target",
        'action': "javascript:alert( 'success!' );"
    }).appendTo(form_group)

    for (const [key, type] of Object.entries(fields)) {

        const newFormGroup2 = $('<div>', {
            'class': 'form-group'
        }).appendTo(newForm)

        newFormGroup2.append($('<label>', {
            'for': key,
            'text': capitalizeFirstLetter(key),
            'class': 'col-form-label',
        }));
        newFormGroup2.append($('<input>', {
            'id': key,
            'name': key,
            'class': 'form-control',
            'type': type
        }));
    }
    const modal_footer = $('<div>', {
        'class': 'modal-footer'
    }).appendTo(modal_content)
    let _class;
    for (const [key, _action] of Object.entries(buttons)) {
        if (key === 'Close') _class = 'btn btn-secondary'
        else if (key === 'Save') _class = 'btn btn-primary'
        else if (key === 'Delete') _class = 'btn btn-danger'
        else _class = 'btn btn-warning'

        modal_footer.append($('<button/>', {
            text: key,
            type: 'button',
            class: _class,
            click: _action
        }));
    }
    $('#modalPlaceholder').html(modal_fade)
}


function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

