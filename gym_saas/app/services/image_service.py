import cloudinary.uploader


class ImageService:

    @staticmethod
    def upload_member_image(file, gym_id, member_id):
        try:
            result = cloudinary.uploader.upload(
                file,
                folder=f"gym_saas/{gym_id}/members",
                public_id=f"member_{member_id}",
                overwrite=True,
                resource_type="image",

                # 🔥 automatic optimization
                quality="auto:eco",  # 🔥 change here
                fetch_format="auto",
                transformation=[{
                    "width": 600,
                    "height": 600,
                    "crop": "limit"
                }])

            return result["secure_url"], None

        except Exception as e:
            return None, str(e)
