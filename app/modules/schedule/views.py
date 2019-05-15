import math

from flask import render_template, flash, request
from flask_login import login_required, current_user

from app import get_logger, get_config
from app import utils
from app.models import Meeting
from . import schedule
from .forms import MeetingForm

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

    dict = {'content': utils.query_to_list(query),
            'total_count': total_count,
            'total_page': math.ceil(total_count / length),
            'page': page,
            'length': length
            }
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


# 会议日程查询
@schedule.route('/schedulelist', methods=['GET', 'POST'])
@login_required
def schedulelist():
    return common_list(Meeting, 'schedulelist.html')


# 会议日程配置
@schedule.route('/scheduleedit', methods=['GET', 'POST'])
@login_required
def scheduleedit():
    return common_edit(Meeting, MeetingForm(), 'scheduleedit.html')
