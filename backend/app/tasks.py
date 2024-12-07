from .celery_app import celery_app
import jieba
from wordcloud import WordCloud
import os

@celery_app.task(name="generate_wordcloud")
def generate_wordcloud(file_path: str):
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 使用结巴分词
        word_list = jieba.cut(text)
        words = ' '.join(word_list)
        
        # 生成词云
        wc = WordCloud(
            font_path='/app/fonts/SimHei.ttf',  # 需要添加中文字体
            width=800,
            height=400,
            background_color='white'
        )
        
        wc.generate(words)
        
        # 保存词云图
        output_path = file_path + '_wordcloud.png'
        wc.to_file(output_path)
        
        return {
            "status": "success",
            "image_path": output_path
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        } 