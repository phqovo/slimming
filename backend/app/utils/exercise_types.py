"""运动类型映射"""

# 小米运动类型中英文映射
XIAOMI_EXERCISE_TYPE_MAP = {
    # 跑步类
    'running': '跑步',
    'outdoor_running': '户外跑步',
    'indoor_running': '室内跑步',
    'treadmill': '跑步机',
    
    # 步行类
    'walking': '步行',
    'outdoor_walking': '户外步行',
    'indoor_walking': '室内步行',
    
    # 骑行类
    'cycling': '骑行',
    'outdoor_cycling': '户外骑行',
    'indoor_cycling': '室内骑行',
    
    # 游泳类
    'swimming': '游泳',
    'pool_swimming': '泳池游泳',
    'open_water_swimming': '开放水域游泳',
    
    # 健身类
    'free_training': '自由训练',
    'strength_training': '力量训练',
    'hiit': '高强度间歇训练',
    'high_interval_training': '高强度间歇训练',
    'core_training': '核心训练',
    'crossfit': 'CrossFit',
    
    # 球类运动
    'basketball': '篮球',
    'football': '足球',
    'badminton': '羽毛球',
    'table_tennis': '乒乓球',
    'tennis': '网球',
    'volleyball': '排球',
    
    # 瑜伽/舞蹈
    'yoga': '瑜伽',
    'dance': '舞蹈',
    'aerobics': '健身操',
    'zumba': '尊巴',
    
    # 户外运动
    'hiking': '登山',
    'climbing': '爬山',
    'trail_running': '越野跑',
    'outdoor_hiking': '户外徒步',
    
    # 其他运动
    'rope_skipping': '跳绳',
    'elliptical': '椭圆机',
    'rowing': '划船机',
    'skiing': '滑雪',
    'skating': '滑冰',
    'boxing': '拳击',
    'martial_arts': '武术',
    'pilates': '普拉提',
    'spinning': '动感单车',
    'stair_climbing': '爬楼梯',
    'other': '其他',
}


def get_exercise_type_cn(exercise_type: str) -> str:
    """
    获取运动类型的中文名称
    :param exercise_type: 英文运动类型
    :return: 中文运动类型，如果找不到则返回原值
    """
    if not exercise_type:
        return '未知运动'
    
    return XIAOMI_EXERCISE_TYPE_MAP.get(exercise_type.lower(), exercise_type)
