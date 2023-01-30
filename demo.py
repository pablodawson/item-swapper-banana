
import banana_dev as banana

model_inputs = {
  "prompt": "A superhero with the body of a banana",
  "height": 512,
  "width": 512,
  "steps": 50,
  "guidance_scale": 9,
  "seed": None
}

api_key = "YOUR_API_KEY"
model_key = "YOUR_MODEL_KEY"

# Run the model
out = banana.run(api_key, model_key, model_inputs)


