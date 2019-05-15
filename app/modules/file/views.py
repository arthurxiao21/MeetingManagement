import math

from flask import render_template, flash, request, abort, send_file, jsonify
from flask_login import login_required, current_user

from app import get_logger, get_config
from app import utils
from app.models import Pastefile
from . import file

ONE_MONTH = 60 * 60 * 24 * 30

logger = get_logger(__name__)
cfg = get_config()


# 通用列表查询
def common_list(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    # 删除操作
    if action == 'del' and id:
        try:
            DynamicModel.get(DynamicModel.id == id).delete_instance()
            flash('删除成功')
        except:
            flash('删除失败')

    # 查询列表
    query = DynamicModel.select()
    total_count = query.count()

    # 处理分页
    if page: query = query.paginate(page, length)

    dict = {'content': utils.query_to_list(query), 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template(view, form=dict, current_user=current_user)


# 通用单模型查询&新增&修改
def common_edit(DynamicModel, form, view):
    id = request.args.get('id', '')
    if id:
        # 查询
        model = DynamicModel.get(DynamicModel.id == id)
        if request.method == 'GET':
            utils.model_to_form(model, form)
        # 修改
        if request.method == 'POST':
            if form.validate_on_submit():
                utils.form_to_model(form, model)
                model.save()
                flash('修改成功')
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            model = DynamicModel()
            utils.form_to_model(form, model)
            model.save()
            flash('保存成功')
        else:
            utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)


# 文件查询
@file.route('/filelist', methods=['GET', 'POST'])
@login_required
def filelist():
    if request.args.get('meetingID') is None or request.args.get('fileName') is None:
        return common_list(Pastefile, 'filelist.html')
    id = request.args.get('id', '')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE
    meetingID = request.args.get('meetingID')
    fileName = request.args.get('fileName')
    query = Pastefile.select()
    if meetingID.strip() != '':
        query = Pastefile.select().where(Pastefile.meetingID == meetingID)
    if fileName.strip() != '':
        query = Pastefile.select().where(Pastefile.fileName == fileName)
    # 查询列表
    total_count = query.count()

    # 处理分页
    if page: query = query.paginate(page, length)

    dict = {'content': utils.query_to_list(query), 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}

    return render_template('filelist.html', form=dict, current_user=current_user)


# 文件上传编辑
@file.route('/fileedit', methods=['GET', 'POST'])
@login_required
def fileedit():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        uploaderID = request.form.get('uploaderID')
        meetingID = request.form.get('meetingID')
        fileName = request.form.get('fileName')
        if not uploaded_file:
            flash("请上传文件")

        else:
            paste_file = Pastefile.create_by_upload_file(uploaded_file)
            paste_file.uploaderID = uploaderID
            paste_file.meetingID = meetingID
            paste_file.fileName = fileName
            paste_file.save()
            flash("文件上传成功")
        # return jsonify({
        #     'url_d': paste_file.url_d,
        #     'url_i': paste_file.url_i,
        #     'url_s': paste_file.url_s,
        #     'url_p': paste_file.url_p,
        #     'filename': paste_file.filename,
        #     'size': humanize_bytes(paste_file.size),
        #     'time': str(paste_file.uploadtime),
        #     'type': paste_file.type,
        #     'quoteurl': paste_file.quoteurl
        # })
    return render_template('fileedit.html', current_user=current_user)


@file.route('/d/<filehash>', methods=['GET'])
def download(filehash):
    paste_file = Pastefile.get_by_filehash(filehash)
    return send_file(open(paste_file.path, 'rb'),
                     mimetype='application/octet-stream',
                     cache_timeout=ONE_MONTH,
                     as_attachment=True,
                     attachment_filename=paste_file.fileHash)


@file.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@file.route('/j', methods=['POST'])
def j():
    uploaded_file = request.files['file']

    if uploaded_file:
        paste_file = Pastefile.create_by_upload_file(uploaded_file)
        paste_file.save()

        return jsonify({
            'url': paste_file.url_i,
            'short_url': paste_file.url_s,
            'origin_filename': paste_file.filename,
            'hash': paste_file.filehash,
        })

    return abort(400)
