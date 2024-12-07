from .celery_app import celery_app
import jieba
from wordcloud import WordCloud
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="generate_wordcloud")
def generate_wordcloud(file_path: str):
    try:
        logger.info(f"开始处理文件: {file_path}")
        
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
        
        # 使用结巴分词
        logger.info("进行分词")
        word_list = jieba.cut(text)
        words = ' '.join(word_list)
        
        # 生成词云图
        logger.info("生成词云图")
        wc = WordCloud(
            font_path='/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',  # 修改字体路径
            width=800,
            height=400,
            background_color='white'
        )
        
        wc.generate(words)
        
        # 生成输出文件路径
        output_filename = Path(file_path).stem + '_wordcloud.png'
        output_path = os.path.join(os.path.dirname(file_path), output_filename)
        
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