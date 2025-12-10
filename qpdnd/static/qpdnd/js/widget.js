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
        this.stop_btn = $("#anncsu_stopSendToPdnd");
        this.progress_bar = $(".progress-bar");
        this.task_id_container = $("#task_id");
        this.task_results_container = $("#task_results");
        this.task_status_container = $("#task_status");
        this.base_url_info_task = null;
        this.base_url_kill_task = null;
        this.task_id = null;
        this.task_results = null;
        this.huey_signals = null;
        this.task_info_interval = null;
    },

    disable_run_btn: function(){
        this.run_btn.prop('disabled', true);
    },

    enable_run_btn: function(){
        this.run_btn.prop('disabled', false);
    },

    disable_stop_btn: function(){
        this.stop_btn.prop('disabled', true);
    },

    enable_stop_btn: function(){
        this.stop_btn.prop('disabled', false);
    },

    stop: function(kill_url){
        var that = this;
        this.stop_btn.on("click", function(){
           
           $.ajax({
                   method: 'get',
                   url: kill_url,
                   success: function (res) {
                       console.log(res);
                       if (res['status'] == that.huey_signals.REVOKED) {
                           that.enable_run_btn();
                           that.disable_stop_btn();
                           that.task_status_container.text(that.huey_signals.REVOKED.toUpperCase());
                           clearInterval(that.task_info_interval);

                           // Wait a moment and get final task info
                           that.show_loading_task_results();
                           setTimeout(function(){
                               that.taskInfoOnceTime();
                           }, 500);
                       } else {
                           throw (res['error_message']);
                       }
                   },
                   error: function (xhr, textStatus, errorMessage) {
                       ga.widget.showError(ga.utils.buildAjaxErrorMessage(xhr.status, errorMessage));
                   }

           });
       });
    },

    run: function(run_url){
         var that = this;
         this.run_btn.on("click", function(){

            // Clear previous results
            that.task_results_container.html('');
            
            $.ajax({
                    method: 'get',
                    url: run_url,
                    success: function (res) {
                        console.log(res);
                        if (res['result']) {
                            that.task_id = res['task_id'];

                            that.disable_run_btn();
                            that.stop("/qpdnd/" + that.base_url_kill_task + that.task_id);
                            that.enable_stop_btn();

                            // Show task id
                            that.task_id_container.text(that.task_id);
                            that.task_status_container.text(that.huey_signals.EXECUTING.toUpperCase());
                            

                            // Start task info polling
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

    taskInfoOnceTime: function(){
        var that = this;
         $.ajax({
                method: 'get',
                url: '/qpdnd/' + that.base_url_info_task + that.task_id + '/',
                success: function (res) {

                    that.task_results = res['task_result'];
                    that.render_task_results();
                },
                error: function (xhr, textStatus, errorMessage) {
                    ga.widget.showError(ga.utils.buildAjaxErrorMessage(xhr.status, errorMessage));
                }
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
                        if (res['status'] == that.huey_signals.EXECUTING) {
                            current_progress = res['progress'];
                            that.progress_bar.css("width", current_progress + "%")
                              .attr("aria-valuenow", current_progress)
                              .text(current_progress + "% Complete");
                        }

                        if (res['progress'] == 100 && res['status'] == that.huey_signals.COMPLETE) {
                            clearInterval(that.task_info_interval);
                            that.progress_bar.css("width",  "100%")
                                .attr("aria-valuenow", '100')
                                .text("100% Complete");

                            that.enable_run_btn();  
                            that.task_status_container.text(res['status'].toUpperCase());
                            that.task_results = res['task_result'];
                            that.render_task_results();
                        }

                        if (res['status'] == 'unknown' || res['status'] == that.huey_signals.INTERRUPTED) {
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

            this.task_info_interval = setInterval(_taskinfo, 1000)


        } catch (e) {
            this.showError(e.message);
        }
    },

    show_loading_task_results: function(){
        this.task_results_container.html('<p>Loading task results...</p>');
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
            </div>
        </div>

        <div class="info-box bg-red">
            <span class="info-box-icon"><i class="ion ion-ios-cloud-download-outline"></i></span>

            <div class="info-box-content">
                <span class="info-box-text">Errors</span>
                <span class="info-box-number"><%= failed %></span>
            </div>
        </div>
    `),
};