from StringIO import StringIO
from base64 import b64decode
from .base import Base

class Icons(Base):
    def runTest(self):
        self.register_test_user("1")
        
        # Add item1:
        rv = self.post_node(type="items", parent="en", name="item1")
        item1 = self.get_newest_node_nid(rv.data)
        
        #>>> b64encode(open("accept.png").read())
        accept_16x16_png = (
        'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAKfSURBVDjLpZPrS1NhHMf9O3bOdmwDCWREIYKEUHsVJBI7mg3FvCxL09290jZj2EyLMnJexkgpLbPUanNOberU5taUM'
        'nHZUULMvelCtWF0sW/n7MVMEiN64AsPD8/n83uucQDi/id/DBT4Dolypw/qsz0pTMbj/WHpiDgsdSUyUmeiPt2+V7SrIM+bSss8ySGdR4abQQv6lrui6VxsRonrGCS9VEjSQ9E7CtiqdOZ4UuTqnBHO1X7YXl6Daa4yGq7vWO1D40wVDtj4kWQbn94myPGkCDPdSesczE2sCZShwl'
        '8CzcwZ6NiUs6n2nYX99T1cnKqA2EKui6+TwphA5k4yqMayopU5mANV3lNQTBdCMVUA9VQh3GuDMHiVcLCS3J4jSLhCGmKCjBEx0xlshjXYhApfMZRP5CyYD+UkG08+xt+4wLVQZA1tzxthm2tEfD3JxARH7QkbD1ZuozaggdZbxK5kAIsf5qGaKMTY2lAU/rH5HW3PLsEwUYy+YCc'
        'ERmIjJpDcpzb6l7th9KtQ69fi09ePUej9l7cx2DJbD7UrG3r3afQHOyCo+V3QQzE35pvQvnAZukk5zL5qRL59jsKbPzdheXoBZc4saFhBS6AO7V4zqCpiawuptwQG+UAa7Ct3UT0hh9p9EnXT5Vh6t4C22QaUDh6HwnECOmcO7K+6kW49DKqS2DrEZCtfuI+9GrNHg4fMHVSO5kE7'
        'nAPVkAxKBxcOzsajpS4Yh4ohUPPWKTUh3PaQEptIOr6BiJjcZXCwktaAGfrRIpwblqOV3YKdhfXOIvBLeREWpnd8ynsaSJoyESFphwTtfjN6X1jRO2+FxWtCWksqBApeiFIR9K6fiTpPiigDoadqCEag5YUFKl6Yrciw0VOlhOivv/Ff8wtn0KzlebrUYwAAAABJRU5ErkJggg==')

        accept_20x20_png = (
        'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAMAAAC6V+0/AAAABGdBTUEAAK/INwWK6QAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAeBQTFRFAAAAYslAXsU7W8I5VL0xUrstUrkrUrcrTrQoYMc9WcI2QqsfQqkfXsU7V'
        'cA0Mp0dNp0dXMI5Vb40LZYcLZQcWb40Jo8cVLstIIgcS7QmHn8bQq0fHnobQqkfH3gbPaQeH3cbNpsdL5YcHnEaH3EbK5EcIIobHWwaH3EbIYocH4MbHm4aH3AbH4EcH34bH3obHnMaHnAaH3EbH3EbH2wbdMJZo9eWrtylodaVarlQkM5/t+GvndiSg853teGui8h4esxtdspqcs'
        'hodMhodchoeclrtN+sicR2cL9XcMdlbsVjbsRiccRjvuO2fsdvtd+sXqlIodeVm9eRdslpb8ZkbsRhb8Nhb8JhwOS5////5vTjmdGLnc6Lsd2ngMxyc8dmt+Gw1u7ScMFjv+O4/P37mdCMfsFprtehr9ymf8pwgMpz8fnw7ffrls2Icblbfb5nr9egn9KRmtSNdMNkh8l59Pry/f7'
        '9lsuGbbdXcrlbl8yFmseHZLBMtN2qecFkcb5fhcV12ezUmc2KbLZWbrVYdLdctNqmTptBh8Jystuod7xgc7pccLhZb7VZb7VYdLdbs9mlf7hpg75ttduomMyHfbxmfLpkmMuGtNmlfbdmUqBCmsqHq9Obq9KblseDTJc9ConzcQAAADV0Uk5TACN92/Pz230jU+bmU1P09FMi5eUi'
        'fn7b2/b29vbb235+IuXlIlP09FNT5uZTI33b8/PbfSPbNyt4AAAAAWJLR0QAiAUdSAAAAAlwSFlzAAAASAAAAEgARslrPgAAANZJREFUGNNjYKAGYGRiZmFlY+dAFuPkMjUzN7ew5OZBiPHyWVnb2Nra2NnzC8DEBIWs7BwcnZxdXN3chUWggqIe1g5Onl7ePr5+/gFiUEHxwKDgk'
        'NCw8IjIqOgYCaigZGxcfEJiUnJkSmpauhRUUDojMys7MicyJTcvv0AGKihbWFRcUhpZVl5RWVUtBxWUr6mtq29obGpuaW1rV4AKKip1dHZ19/T29U+YqKwCc6iq2qTJU6ZOmz5jproGwkuaWrNmz5k7b762DrLndfX0DQyNjE2oEroA6kY1Xjs56jEAAAAldEVYdGRhdGU6Y3JlYX'
        'RlADIwMTItMDQtMjVUMjE6NDk6MjErMDI6MDAtS1deAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDA2LTAzLTEyVDIxOjQ4OjE0KzAxOjAwXllSGAAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAAASUVORK5CYII=')

        # Set custom icon 16x16 PNG:
        rv = self.client.post("/icon/%s" % item1, data={"use": "custom", "icon": (StringIO(b64decode(accept_16x16_png)), "accept.png")}, follow_redirects=True)
        assert "Set icon successfully." in rv.data
        assert accept_16x16_png in rv.data
        
        # Set icon with different file extension from "png":
        rv = self.client.post("/icon/%s" % item1, data={"use": "custom", "icon": (StringIO(b64decode(accept_16x16_png)), "accept.PNG")}, follow_redirects=True)
        assert "File extension PNG is not allowed. Allowed extension is png." in rv.data
        
        # Set original icon:
        rv = self.client.post("/icon/%s" % item1, data={"use": "default", "icon": (None, "")}, follow_redirects=True)
        assert "Set icon successfully." in rv.data
        
        # Try to set 20x20x PNG:
        rv = self.client.post("/icon/%s" % item1, data={"use": "custom", "icon": (StringIO(b64decode(accept_20x20_png)), "accept.png")}, follow_redirects=True)
        assert "Image size 20x20 is not allowed. Allowed image size is: 16x16." in rv.data
        
        # Try to set text file with png extension:
        rv = self.client.post("/icon/%s" % item1, data={"use": "custom", "icon": (StringIO("some text"), "text.png")}, follow_redirects=True)
        assert "Mime-type text/plain is not allowed. Allowed mime-type is image/png." in rv.data
        