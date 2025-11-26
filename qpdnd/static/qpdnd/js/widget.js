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

/// For ANNCSU project
ga.QPDND.ANNCSU = {

    init: function(){
        this.run_btn = $("#anncsu_sendToPdnd");
        this.progress_bar = $(".progress-bar");
        this.task_id_container = $("#task_id");
        this.task_status_container = $("#task_status");
        this.base_url_info_task = null;
        this.task_id = null;
    },

    disable_run_btn: function(){
        this.run_btn.prop('disabled', true);
    },

    run: function(run_url){
         var that = this;
         this.run_btn.on("click", function(){
            
            $.ajax({
                    method: 'get',
                    url: run_url,
                    success: function (res) {
                        console.log(res);
                        if (res['result']) {
                            that.task_id = res['task_id'];

                            that.disable_run_btn();
                            // Show task id
                            that.task_id_container.text(that.task_id);
                            that.task_status_container.text('EXECUTING');
                            

                            that.taskInfo();
                        } else {
                            throw Error(res['error_message']);
                        }
                    },
                    error: function (xhr, textStatus, errorMessage) {
                        ga.widget.showError(ga.utils.buildAjaxErrorMessage(xhr.status, errorMessage));
                    }

            });
        });
    },

    taskInfo: function(){
        try {           
            var that = this;
            //call ajax info url
            var _taskinfo = function () {
                $.ajax({
                    method: 'get',
                    url: '/qpdnd/' + that.base_url_info_task + that.task_id + '/',
                    success: function (res) {
                        var current_progress = 0;
                        if (res['status'] == 'executing' || res['status'] == 'PENDING') {
                            current_progress = res['progress'];
                            that.progress_bar.css("width", current_progress + "%")
                              .attr("aria-valuenow", current_progress)
                              .text(current_progress + "% Complete");
                        }

                        if (current_progress >= 100 || res['status'] == 'SUCCESS' || res['status'] == 'complete') {
                          clearInterval(interval);
                          that.progress_bar.css("width",  "100%")
                              .attr("aria-valuenow", '100')
                              .text("100% Complete");

                        //   //reload page after 1sec
                        //   setTimeout(function(){
                        //        window.location.reload(1);
                        //        }, 5000);
                        }

                        if (res['status'] == 'UNKNOWN' || res['status'] == 'unknown') {
                            //reload page after 1sec
                            setTimeout(function(){
                               window.location.reload(1);
                               }, 5000);
                        }
                    },
                    error: function (xhr, textStatus, errorMessage) {
                        ga.widget.showError(ga.utils.buildAjaxErrorMessage(xhr.status, errorMessage));
                    }


                });
            };

            var interval = setInterval(_taskinfo, 1000)


        } catch (e) {
            this.showError(e.message);
        }
    },
};