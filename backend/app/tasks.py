from .celery_app import celery_app
from .config import settings  # 导入配置
import jieba
from wordcloud import WordCloud
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_stop_words():
    try:
        # 使用固定的停用词文件路径
        stop_words_path = os.path.join(os.path.dirname(__file__), 'stop_words.txt')
        logger.info(f"加载停用词文件: {stop_words_path}")
        with open(stop_words_path, 'r', encoding='utf-8') as f:
            return set([line.strip() for line in f.readlines()])
    except Exception as e:
        logger.error(f"加载停用词失败: {str(e)}")
        return set()


# 全局停用词集合
STOP_WORDS = load_stop_words()


@celery_app.task(name="generate_wordcloud")
def generate_wordcloud(file_path: str):
    try:
        logger.info(f"开始处理文件: {file_path}")
        logger.info(f"当前停用词数量: {len(STOP_WORDS)}")
        
        # 确保文件存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return {
                "status": "error",
                "error": "文件不存在"
            }

        # 读取文件内容
        logger.info("读取文件内容")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 使用结巴分词并过滤停用词
        logger.info("进行分词")
        word_list = list(jieba.cut(text))
        logger.info(f"分词前总词数: {len(word_list)}")
        
        # 过滤停用词
        filtered_words = [
            word for word in word_list 
            if word.strip() and word not in STOP_WORDS
        ]
        logger.info(f"过滤后词数: {len(filtered_words)}")
        words = ' '.join(filtered_words)
        
        # 生成词云图
        logger.info("生成词云图")
        wc = WordCloud(
            font_path='/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',
            width=800,
            height=400,
            colormap='rainbow',
            background_color='white',
            stopwords=STOP_WORDS
        )
        
        wc.generate(words)
        
        # 使用配置中的上传目录
        output_filename = Path(file_path).stem + '_wordcloud.png'
        output_path = os.path.join(settings.UPLOAD_FOLDER, output_filename)
        
        # 保存词云图
        logger.info(f"保存词云图到: {output_path}")
        wc.to_file(output_path)
        
        # 返回相对路径
        relative_path = os.path.basename(output_path)
        logger.info(f"处理完成，返回路径: {relative_path}")
        
        return {
            "status": "success",
            "image_path": relative_path
        }
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        } 