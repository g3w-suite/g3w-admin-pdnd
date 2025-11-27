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
        this.task_results_container = $("#task_results");
        this.task_status_container = $("#task_status");
        this.base_url_info_task = null;
        this.task_id = null;
        this.task_results = null;
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

    render_task_results: function(){

        if (this.task_results){
            var total = this.task_results['success'] + this.task_results['failed'];
            var perc_success = total > 0 ? (this.task_results['success'] / total * 100).toFixed(2) : 0;
            var perc_failed = total > 0 ? (this.task_results['failed'] / total * 100).toFixed(2) : 0;
            
            this.task_results_container.html(this.template_task_results({
                success: this.task_results['success'],
                failed: this.task_results['failed'],
                perc_success: perc_success,
                perc_failed: perc_failed,
            }));
        }
    },

    template_task_results: _.template(`
        <div class="info-box bg-green">
            <span class="info-box-icon"><i class="ion ion-ios-heart-outline"></i></span>

            <div class="info-box-content">
                <span class="info-box-text">Feature sent</span>
                <span class="info-box-number"> <%= success %></span>

                <div class="progress">
                    <div class="progress-bar" style="width: <%= perc_success %>%"></div>
                </div>
                <span class="progress-description">
                    <%= perc_success %>%                 
                </span>
            </div>
        </div>

        <div class="info-box bg-red">
            <span class="info-box-icon"><i class="ion ion-ios-cloud-download-outline"></i></span>

            <div class="info-box-content">
                <span class="info-box-text">Errors</span>
                <span class="info-box-number"><%= failed %></span>

                <div class="progress">
                    <div class="progress-bar" style="width: <%= perc_failed %>%"></div>
                </div>
                <span class="progress-description">
                    <%= perc_failed %>%
                </span>
            </div>
        </div>
    `),
};