from datasets import load_metric


class RougeMetrics:
    def __init__(self, tokenizer):
        self.__rouge = load_metric("rouge")
        self.__tokenizer = tokenizer

    def compute_metrics(self, pred):
        labels_ids = pred.label_ids
        pred_ids = pred.predictions

        # all unnecessary tokens are removed
        pred_str = self.__tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
        labels_ids[labels_ids == -100] = self.__tokenizer.pad_token_id
        label_str = self.__tokenizer.batch_decode(labels_ids, skip_special_tokens=True)

        rouge_output = self.__rouge.compute(predictions=pred_str, references=label_str, rouge_types=["rouge2"])["rouge2"].mid

        return {
            "rouge2_precision": round(rouge_output.precision, 4),
            "rouge2_recall": round(rouge_output.recall, 4),
            "rouge2_fmeasure": round(rouge_output.fmeasure, 4),
        }
