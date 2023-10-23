python bonus.py \
  --model_name_or_path "hfl/chinese-xlnet-base" \
  --train_file "$1" \
  --validation_file "$2" \
  --context_file "$3"\
  --max_seq_length 1024 \
  --output_dir "$4" \
  --per_device_train_batch_size 2 \
  --gradient_accumulation_steps 2 \
  --learning_rate 5e-5 \
  --num_train_epochs 1 \
  --with_tracking 
