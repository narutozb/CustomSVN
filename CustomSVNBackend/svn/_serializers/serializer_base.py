from rest_framework import serializers


class SoloSerializer(serializers.ModelSerializer):
    '''
    专门用于描述特定类的序列器
    例如描述FileChange的详情信息，或者Commit的详情信息，都需要继承此类
    子类的名字应该为"类名QuerySoloSerializer"
    '''