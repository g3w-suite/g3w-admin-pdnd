/**
 * Created by Walter Lorenzetti (lorenzetti@gis3w.it)
 */

ga.QPDND = {
    init: function(){
        var $form = $("#qpdnd-project-form");
        this.project_select = $form.find('#id_project');
        this.contact_author = $form.find('#id_contact_author');
        this.contact_email = $form.find('#id_contact_email');
        this.contact_url = $form.find('#id_contact_url');

        this.title = $form.find('#id_title');
        this.abstract = $form.find('#id_description');

        this.set_current_project();
        this.bind_project();
    },

    /**
     * Set the state of form, insert/update
     * @param mode
     */
    set_form_mod: function (mode='insert'){
      this.form_state = mode;
    },

    /**
     * Set the API url to call for get information about Qgis Project metadata
     * @param url
     */
    set_project_info_url(url){
        this.project_info_url = url;
    },

    /**
     * Gte current project selected
     */
    get_current_project: function(){
        return this.project_select.val();
    },

    /**
     * Set the current project ina property
     */
    set_current_project: function(){
        this.current_project = this.get_current_project();
    },

    bind_project: function(){
        var that = this;
        this.project_select.on("change", function(){

            var current_val = $(this).val();
            if (that.form_state == 'update' && current_val == that.current_val){
                return false;
            }

            var url = that.project_info_url + current_val;
            $.get(url, function(data){

                console.log(data);
                that.contact_author.val(data['ContactPerson']);
                that.contact_email.val(data['ContactMail']);
                that.contact_url.val(data['OnlineResource']);

                that.title.val(data['Title']);
                that.abstract.val(data['Abstract'])



            });

        });
    }
}